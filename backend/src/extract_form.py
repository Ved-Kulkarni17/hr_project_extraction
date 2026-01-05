import pdfplumber

def extract_form_based_fields(pdf_path):
    data = {"doc_type": "form", "bank_name": None}
    
    with pdfplumber.open(pdf_path) as pdf:
        if not pdf.pages: return data
        page = pdf.pages[0]
        tables = page.extract_tables()
        
        if tables:
            for table in tables:
                for row in table:
                    if len(row) < 2: continue
                    key = str(row[0]).strip().lower().replace(":", "") if row[0] else ""
                    val = str(row[1]).strip() if row[1] else ""
                    
                    if "candidate id" in key: data["candidate_id"] = val
                    elif "email" in key: 
                        data["email"] = val
                        if "candidate_id" not in data: data["candidate_id"] = val
                    elif "full name" in key or "name" == key: data["full_name"] = val
                    elif "phone" in key: data["phone_number"] = val
                    elif "role" in key: data["role"] = val
                    elif "joining" in key or "doj" in key: data["date_of_joining"] = val
                    elif "location" in key: data["location"] = val
                    elif "age" in key: data["age"] = val
                    elif "bank name" in key: data["bank_name"] = val
                    elif "ifsc" in key: data["ifsc_code"] = val
                    elif "t-shirt" in key: data["t_shirt_size"] = val # NEW
                    
                    elif "account number" in key and val:
                        clean = "".join(filter(str.isdigit, val))
                        # if len(clean) > 4: data["account_number"] = "****" + clean[-4:]
                        # else: data["account_number"] = "****" + clean
                        data["account_number"] = clean

    return data
