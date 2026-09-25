import re


date_pattern_1 = r'[A-Za-z]+\s\d{1,2}\s\d{4}'      # August 06 2025
date_pattern_2 = r'\d{1,2}/\d{1,2}/\d{4}'           # 5/11/2024
date_pattern_3 = r'\d{4}-\d{1,2}-\d{1,2}'           # 2024-11-05
date_pattern_4 = r'\d{1,2}/\d{1,2}/\d{2}\b'         # 09/14/26

money_pattern = r'\d{1,3}(,\d{3})*\.\d{2}'          # 51,604.00


def parse_receipt(text_list):
    store_name = None
    date = None

    uppercase_candidate = None
    titlecase_cadidate = None

    date_patterns = [date_pattern_1, date_pattern_2, date_pattern_3, date_pattern_4]

    money_matches = [] # will hold (index, text) for every money match

    for i, text in enumerate(text_list):
        for pattern in date_patterns: 
            if re.search(pattern, text): # reuse this for validating date
                date = text

        if re.search(money_pattern, text): #reuse this for for validating money
            money_matches.append((i, text))   # now both total and its index is saved to the money match list(the position)

        has_digit = any(char.isdigit() for char in text)   # validation for store name
        
        letter_count = sum(char.isalpha() for char in text)
        is_mostly_letters = len(text) > 4 and letter_count / len(text) > 0.7
        if is_mostly_letters and not has_digit:
            if uppercase_candidate is None and text.isupper():
                uppercase_candidate = text
            if titlecase_cadidate is None and text.istitle():
                titlecase_cadidate = text

            
    if uppercase_candidate is not None:
        store_name = uppercase_candidate
    else:
        store_name = titlecase_cadidate
    

    total = None
    total_index = None
    for i, value in money_matches:
        if i > 0 and "total" in text_list[i - 1].lower():
            total = value
            total_index = i

    # Fallback: if no "total"-labeled match found, use the last money match
    if total is None and money_matches:
        total_index, total = money_matches[-1]

    excluded_keywords = ["total", "subtotal", "%", "mastercard", "visa", "cash", "card", "debit", "credit"]

    items = []
    for i, text in money_matches:
        if i != total_index and i > 0:
            item_name = text_list[i - 1]

            # If the "name" is purely numeric (likely a barcode), try the fragment before THAT instead
            if item_name.strip().isdigit() and i > 1:
                item_name = text_list[i - 2]

            if not any(keyword in item_name.lower() for keyword in excluded_keywords):
                items.append({"name": item_name, "price": text}) # price is the text is reused here!

    return {"store_name": store_name, "date": date, "total": total, "items": items}


if __name__ == "__main__":
    sample_text = [
        "14.20", "X1 Vol", "R8/6", "4G ,ll 0 47%", "rtal conestogac.on.ca",
        "", "College", "C", "CONESTOGA", "Institute 0f Technology & Advanced Leurning",
        "299 Doon Valley"
    ]