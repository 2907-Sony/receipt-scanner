# Receipt Scanner

Take a photo of a receipt and get the store, date, total and line items saved to a searchable history.

**Live demo:** https://receipt-scanner-three-eta.vercel.app
**API docs:** https://receipt-scanner-docker.onrender.com/docs

> The backend runs on a free tier and sleeps after ~15 minutes idle. The first request can take about a minute to wake it up, and a scan can take 20-60 seconds.

## What it does

- Upload a receipt photo or take one with your phone camera
- Extracts the store name, purchase date, total and individual items
- Saves everything to a database and lets you browse and search past receipts

## Tech stack

| Layer | Tools |
|---|---|
| Frontend | React, Vite, deployed on Vercel |
| Backend | FastAPI (Python), SQLAlchemy, deployed in Docker on Render |
| Database | PostgreSQL (Neon) |
| OCR | Tesseract via pytesseract, with Pillow preprocessing |
| NLP | spaCy custom NER model (COMPANY, DATE, TOTAL), trained on the SROIE receipt dataset |

## How it works

1. **Preprocess:** fix phone-photo rotation, convert to grayscale, boost contrast, and resize large or small images.
2. **OCR:** Tesseract reads the image into text lines.
3. **Extract fields with layered fallbacks:**
   - **Store:** known-store lookup (with fuzzy matching for OCR typos) -> NER model -> first-word fallback -> regex
   - **Total:** NER model -> the line starting with `TOTAL` -> regex
   - **Date:** NER model -> regex -> a forgiving date finder that tolerates OCR errors (for example `/` read as `7`)
   - **Items:** per-line pattern matching, excluding tax, totals and payment lines
4. **Save:** the receipt and its items are stored in PostgreSQL and returned to the UI.

## Design decisions and trade-offs

- **Tesseract instead of EasyOCR.** I started with EasyOCR (PyTorch), which read photos more accurately, but it didn't fit the 512 MB RAM of a free web service. I switched to Tesseract, which is much lighter, and made up for it with image preprocessing and more robust parsing. This also taught me how tightly the parsing depended on the OCR's output shape: EasyOCR returns one entry per text box, while Tesseract returns one merged line per row, so I rewrote the item extraction around lines.
- **Layered fallbacks instead of trusting one model.** The NER model was trained on Malaysian receipts, so it often misses on Canadian ones (domain shift). Each field therefore has a fallback chain, and a store dictionary with fuzzy matching handles the most common stores.
- **Non-blocking upload endpoint.** OCR is slow, blocking work. Running it in FastAPI's threadpool keeps the server answering health checks, which fixed a bug where the platform killed the app mid-scan.

## Known limitations

- Accuracy depends on photo quality. A raw phone photo (receipt small in frame, background, tilt, shadows) reads worse than a cropped, flat scan. For best results, use a document-scanner app or crop the receipt before uploading.
- OCR on faint thermal-paper text or angled, dim photos is imperfect, so some item names are misread or missed.
- The store name for stores outside the known list falls back to the first word on the receipt.
- The NER model is trained on a different country's receipts, so it is mainly a first attempt, with the rules behind it doing most of the work.
- Tested on [ ] real receipts: store correct [ ]/[ ], total correct [ ]/[ ], date correct [ ]/[ ].
- Free-tier hosting means slow cold starts.

## Run locally

Backend:
```
cd backend
pip install -r requirements.txt
# install Tesseract first (macOS: brew install tesseract)
# create backend/.env with DATABASE_URL=<your Postgres connection string>
uvicorn main:app --reload
```

Frontend:
```
cd frontend
npm install
npm run dev
```

Set `VITE_API_URL` to point the frontend at a deployed backend (it defaults to `http://127.0.0.1:8000`).

## Possible improvements

- Add an in-app crop step so users can select just the receipt before uploading (biggest expected accuracy gain for camera photos)
- Better OCR engine or a hosted OCR API for higher accuracy
- Let users correct misread fields in the UI
- Retrain the NER model on Canadian receipts
- Spending summaries by store and month
