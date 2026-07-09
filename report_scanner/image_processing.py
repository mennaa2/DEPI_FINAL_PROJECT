"""
Image processing for the Medical Report Scanner.

Takes a raw upload (phone photo or PDF) and turns it into the cleanest
possible image(s) for OCR:

    * PDF pages are rendered to images (or their embedded text is read
      directly, when present, which is faster and more accurate than OCR).
    * Photos are auto-rotated, denoised, contrast-enhanced, sharpened,
      and — where a clear document boundary can be found — cropped to
      just the page.

Every step is best-effort: if a step fails (e.g. no document boundary
can be detected in a busy background), we fall back to the previous,
less-processed version rather than raising, so a messy phone photo still
gets *some* OCR attempt instead of none.
"""

import io
import numpy as np
import cv2
from PIL import Image, ImageOps

SUPPORTED_IMAGE_TYPES = {"jpg", "jpeg", "png"}
SUPPORTED_TYPES = SUPPORTED_IMAGE_TYPES | {"pdf"}


class UnsupportedFileError(Exception):
    """Raised when an uploaded file isn't a supported image or PDF."""


def _pil_to_cv2(pil_img: Image.Image) -> np.ndarray:
    rgb = np.array(pil_img.convert("RGB"))
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def _cv2_to_pil(cv_img: np.ndarray) -> Image.Image:
    rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)


# -----------------------------------------------------------------------
# Loading uploads
# -----------------------------------------------------------------------
def load_pages_from_upload(uploaded_file) -> list:
    """
    Turn a Streamlit UploadedFile into a list of PIL images — one per
    page. Images produce a single-item list; PDFs may produce several.

    Raises UnsupportedFileError for anything else.
    """
    name = (uploaded_file.name or "").lower()
    ext = name.rsplit(".", 1)[-1] if "." in name else ""

    if ext in SUPPORTED_IMAGE_TYPES:
        img = Image.open(uploaded_file)
        img = ImageOps.exif_transpose(img)  # respect phone camera orientation
        return [img.convert("RGB")]

    if ext == "pdf":
        return _load_pdf_pages(uploaded_file.getvalue())

    raise UnsupportedFileError(
        f"Unsupported file type '.{ext or '?'}'. Please upload a JPG, JPEG, "
        "PNG, or PDF file."
    )


def _load_pdf_pages(pdf_bytes: bytes) -> list:
    """Render every page of a PDF to a PIL image using PyMuPDF."""
    import fitz  # PyMuPDF — imported lazily so a missing install only

    pages = []
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    try:
        for page in doc:
            # Render at ~2x zoom for sharper OCR input.
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            pages.append(img)
    finally:
        doc.close()

    if not pages:
        raise UnsupportedFileError("The PDF appears to have no pages.")
    return pages


def extract_pdf_text_layer(pdf_bytes: bytes) -> str:
    """
    Try to read a PDF's embedded text layer directly (fast, no OCR
    needed, near-perfect accuracy). Returns '' if the PDF has no text
    layer (i.e. it's a scanned image) or PyMuPDF isn't available.
    """
    try:
        import fitz
    except ImportError:
        return ""

    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        try:
            text = "\n".join(page.get_text() for page in doc)
        finally:
            doc.close()
        return text.strip()
    except Exception:
        return ""


# -----------------------------------------------------------------------
# Enhancement pipeline
# -----------------------------------------------------------------------
def _auto_rotate(cv_img: np.ndarray) -> np.ndarray:
    """
    Use Tesseract's orientation-and-script detection to auto-rotate the
    image if it's sideways or upside down. Falls back to the original
    orientation if OSD can't confidently determine one (common for
    low-text or very blurry images).
    """
    try:
        import pytesseract

        osd = pytesseract.image_to_osd(cv_img)
        angle_line = [l for l in osd.split("\n") if "Rotate:" in l]
        if angle_line:
            angle = int(angle_line[0].split(":")[1].strip())
            if angle in (90, 180, 270):
                rotate_code = {
                    90: cv2.ROTATE_90_COUNTERCLOCKWISE,
                    180: cv2.ROTATE_180,
                    270: cv2.ROTATE_90_CLOCKWISE,
                }[angle]
                return cv2.rotate(cv_img, rotate_code)
    except Exception:
        pass
    return cv_img


def _denoise_and_contrast(cv_img: np.ndarray) -> np.ndarray:
    """Grayscale + denoise + CLAHE contrast boost + mild sharpening."""
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

    denoised = cv2.fastNlMeansDenoising(gray, h=10, templateWindowSize=7, searchWindowSize=21)

    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    contrasted = clahe.apply(denoised)

    sharpen_kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened = cv2.filter2D(contrasted, -1, sharpen_kernel)

    return cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)


def _detect_and_crop_document(cv_img: np.ndarray) -> np.ndarray:
    """
    Best-effort document-boundary detection: find the largest
    roughly-rectangular contour and perspective-warp it flat. Returns
    the original image unchanged if no confident boundary is found —
    this keeps busy backgrounds (a report photographed on a desk) from
    breaking the pipeline.
    """
    try:
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        edges = cv2.dilate(edges, np.ones((5, 5), np.uint8), iterations=2)

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return cv_img

        largest = max(contours, key=cv2.contourArea)
        img_area = cv_img.shape[0] * cv_img.shape[1]

        # Require the candidate document to cover a meaningful portion of
        # the frame — otherwise this is probably noise, not a page.
        if cv2.contourArea(largest) < 0.25 * img_area:
            return cv_img

        peri = cv2.arcLength(largest, True)
        approx = cv2.approxPolyDP(largest, 0.02 * peri, True)

        if len(approx) != 4:
            return cv_img

        pts = approx.reshape(4, 2).astype("float32")
        rect = _order_points(pts)
        (tl, tr, br, bl) = rect

        width_a = np.linalg.norm(br - bl)
        width_b = np.linalg.norm(tr - tl)
        max_width = max(int(width_a), int(width_b))

        height_a = np.linalg.norm(tr - br)
        height_b = np.linalg.norm(tl - bl)
        max_height = max(int(height_a), int(height_b))

        if max_width < 100 or max_height < 100:
            return cv_img

        dst = np.array(
            [[0, 0], [max_width - 1, 0], [max_width - 1, max_height - 1], [0, max_height - 1]],
            dtype="float32",
        )
        matrix = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(cv_img, matrix, (max_width, max_height))
        return warped
    except Exception:
        return cv_img


def _order_points(pts: np.ndarray) -> np.ndarray:
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]  # top-left
    rect[2] = pts[np.argmax(s)]  # bottom-right
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # top-right
    rect[3] = pts[np.argmax(diff)]  # bottom-left
    return rect


def preprocess_for_ocr(pil_img: Image.Image, crop_document: bool = True) -> Image.Image:
    """
    Full enhancement pipeline for a single page/photo:
    auto-rotate -> (optional) crop to document -> denoise/contrast/sharpen.

    Returns a PIL image ready to hand to the OCR engine. Never raises —
    any stage that fails is skipped, so the caller always gets *an*
    image back.
    """
    cv_img = _pil_to_cv2(pil_img)

    cv_img = _auto_rotate(cv_img)

    if crop_document:
        cv_img = _detect_and_crop_document(cv_img)

    cv_img = _denoise_and_contrast(cv_img)

    return _cv2_to_pil(cv_img)
