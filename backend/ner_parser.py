def parse_receipt_ner(text_list, ner_model):

    full_text = " ".join(text_list)
    doc = ner_model(full_text)

    store_name = None
    date = None
    total = None

    for ent in doc.ents:
        if ent.label_ == "COMPANY":
            store_name = ent.text
        elif ent.label_ == "DATE":
            date = ent.text
        elif ent.label_ == "TOTAL":
            total = ent.text


    return {"store_name": store_name, "date": date, "total": total}
