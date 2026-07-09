"""
Medical Report Scanner package.

Turns an uploaded lab-report photo or PDF into structured medical values:

    image_processing.py -> cleans up the raw upload (rotation, contrast,
                            denoise, sharpen, crop) so OCR has the best
                            possible input
    ocr.py              -> reads text from the cleaned image (EasyOCR
                            preferred, Tesseract fallback)
    report_parser.py     -> regex/NLP-lite extraction of medical values
                            from the raw OCR text
    medical_summary.py   -> turns extracted values into a plain-language
                            summary a pregnant patient can understand
    database.py          -> persistence for scanned reports (separate
                            from, but linked to, the main app database)
"""
