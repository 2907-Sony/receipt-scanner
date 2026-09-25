from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import easyocr
from parser import parse_receipt 
from database import SessionLocal
from models import Receipt, ReceiptItem
from datetime import datetime
import spacy
from ner_parser import parse_receipt_ner


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ner_model = spacy.load("receipt_ner_model")

reader = easyocr.Reader(['en'])

date_formats = ["%B %d %Y", "%m/%d/%Y", "%Y-%m-%d", "%m/%d/%y"]


@app.post("/upload")
async def upload_receipt(file: UploadFile = File(...)):
    contents = await file.read()
    result = reader.readtext(contents)
    extracted_text = [text for (bbox, text, prob) in result]
    parsed_data = parse_receipt(extracted_text)
    ner_result = parse_receipt_ner(extracted_text, ner_model)

    # Fallback for store_name and total: prefer NER, fall back to regex
    final_store_name = ner_result["store_name"] if ner_result["store_name"] is not None else parsed_data["store_name"]
    final_total_str = ner_result["total"] if ner_result["total"] is not None else parsed_data["total"]

    # Date: try NER's date first, and only fall back to regex if NER's date fails to PARSE
    parsed_date = None

    if ner_result["date"] is not None:
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(ner_result["date"], fmt).date()
                break
            except ValueError:
                continue

    if parsed_date is None and parsed_data["date"] is not None:
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(parsed_data["date"], fmt).date()
                break
            except ValueError:
                continue

    cleaned_total = final_total_str.replace(",", "").replace("$", "")
    parsed_total = float(cleaned_total)

    db = SessionLocal()

    new_receipt = Receipt(
        store_name=final_store_name,
        purchase_date=parsed_date,
        total_amount=parsed_total
    )

    db.add(new_receipt)
    db.commit()
    new_receipt_id = new_receipt.id

    for item in parsed_data["items"]:
        cleaned_price = item["price"].replace(",", "")
        try:
            item_price = float(cleaned_price)
        except ValueError:
            continue

        new_item = ReceiptItem(
            receipt_id=new_receipt.id,
            item_name=item["name"],
            item_price=item_price
        )
        db.add(new_item)

    db.commit()
    db.close()

    return {"message": "Receipt saved successfully!", "receipt_id": new_receipt_id}


@app.get("/receipts")
def get_receipts():
    db = SessionLocal()
    receipts = db.query(Receipt).all()
    db.close()
    return receipts


@app.get("/receipts/search")
def search_receipts(store_name: str):
    db = SessionLocal()
    receipts = db.query(Receipt).filter(Receipt.store_name.ilike(f"%{store_name}%")).all()
    db.close()
    return receipts


@app.get("/receipts/{receipt_id}")
def get_receipt(receipt_id: int):
    db = SessionLocal()
    receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
    if receipt is None:
        raise HTTPException(status_code=404, detail="Receipt Not Found")

    
    items_list = [
        {"id": item.id, "item_name": item.item_name, "item_price": item.item_price}
        for item in receipt.items
    ]

    result = {
        "id": receipt.id,
        "store_name": receipt.store_name,
        "purchase_date": receipt.purchase_date,
        "total_amount": receipt.total_amount,
        "created_at": receipt.created_at,
        "items": items_list
    }

    db.close()
    return result


@app.get("/")
def read_root():
    return {"Status": "API is Running Successfully!"}