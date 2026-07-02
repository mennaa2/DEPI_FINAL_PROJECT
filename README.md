# Maternal Care Platform — Premium Redesign

This is a visual redesign of the original Streamlit app. **No ML logic,
prediction logic, or backend behavior was changed** — only the frontend.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## What changed (frontend only)

- `assets/style.css` — full design-system rewrite: pink/purple gradients,
  glassmorphism, animations, custom-styled inputs/buttons/charts, Streamlit
  chrome hidden.
- `utils/components.py` — new shared UI helpers (navbar, footer, hero,
  cards, step wizard, result card, progress ring). `utils/style.py` is kept
  only as a backward-compatible re-export.
- `app.py` — rebuilt as a SaaS-style landing page (hero, features grid,
  "how it works", disclaimer, footer).
- `pages/1_Risk_Prediction.py` — same model, same input columns, same
  `model.predict()` call — now presented as a 4-step wizard with a
  colored result card. `model.predict_proba()` is used **only** to show
  a confidence percentage; it does not affect the predicted class.
- `pages/2_Pregnancy_Tracker.py` — same date/week/due-date math, same
  weekly content — now with a progress ring and timeline.
- `pages/3_Health_Tips.py` — same condition data — selectbox replaced
  with clickable cards.
- `pages/4_AI_Assistant.py` — same FAQ keyword-matching logic — now a
  ChatGPT-style chat UI with history and suggested-question chips.
- `pages/5_About.py` — same content — restyled as a hero + timeline +
  team-card layout.

## Notes on navigation

Streamlit multipage apps route between pages via full page loads, so the
top navbar uses real `st.page_link` navigation (sticky, pill-styled) for
Prediction / Tracker / AI Assistant / Health Tips / About, and an in-page
anchor for "Features" on the home page.
