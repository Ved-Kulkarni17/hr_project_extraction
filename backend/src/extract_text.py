import re
from pypdf import PdfReader

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text

def extract_text_based_fields(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    data = {"doc_type": "text"}
    clean_text = re.sub(r'\s+', ' ', text).strip()

    # --- COMMON ---
    email = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    if email:
        data["email"] = email.group(0)
        data["candidate_id"] = email.group(0) # Default ID

    cid = re.search(r"Candidate ID[:\s]*(\d+)", text, re.IGNORECASE)
    if cid: data["candidate_id"] = cid.group(1)

    name = re.search(r"(?:Name|To|I)[:\s]+([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)", text)
    if name: data["full_name"] = name.group(1)

    phone = re.search(r"(?:Phone|Mobile)[:\s]*([6-9]\d{9})", text)
    if phone: data["phone_number"] = phone.group(1)

    # --- MANAGER EXTRACTION ---
    # Looks for "Reporting Manager: Name" or "reporting to: Name"
    mgr = re.search(r"(?:Reporting Manager|reporting to)[:\s]+([A-Za-z\s]+?)(?:\.|,|\n)", text, re.IGNORECASE)
    if mgr:
        # Clean up any trailing chars
        clean_mgr = mgr.group(1).strip().rstrip(".")
        data["reporting_manager"] = clean_mgr

    # --- AADHAR ---
    if "aadhar" in clean_text.lower():
        data["doc_type"] = "aadhar"
        uid = re.search(r"(?:Number|No)[:\s]*([\d\s]{12,16})", text, re.IGNORECASE)
        if uid:
            raw = uid.group(1).replace(" ", "").replace("\n", "")
            if len(raw) >= 12:
                data["aadhar_number"] = raw
        
        age = re.search(r"Age[:\s]*(\d{2})", text, re.IGNORECASE)
        if age: data["age"] = age.group(1)

    # --- RESUME ---
    elif "experience" in clean_text.lower() and "education" in clean_text.lower():
        data["doc_type"] = "resume"
        exp = re.search(r"(\d+)\s+years", text, re.IGNORECASE)
        if exp: data["experience_years"] = exp.group(1)
        
        cgpa = re.search(r"CGPA[:\s]*([\d\.]+)", text, re.IGNORECASE)
        if cgpa: data["cgpa"] = cgpa.group(1)
        
        for deg in ["B.Tech", "M.Tech", "MBA", "B.Com", "B.Des"]:
            if deg in text: 
                data["education"] = deg; break

        # Resume often has Role
        role = re.search(r"Current Role[:\s]*([A-Za-z\s]+)", text)
        if role: data["role"] = role.group(1).strip()

    # --- LETTERS ---
    else:
        # Role precise extraction
        role = re.search(r"position of\s+(.+?)\s+(?:based|at|starting)", clean_text, re.IGNORECASE)
        if role: data["role"] = role.group(1).strip()

        doj = re.search(r"(?:Joining Date|DOJ|starting)[:\s-]*(\d{4}-\d{2}-\d{2})", text, re.IGNORECASE)
        if doj: data["date_of_joining"] = doj.group(1)

        loc = re.search(r"Location[:\s-]*([A-Za-z]+)", text, re.IGNORECASE)
        if not loc: loc = re.search(r"based in\s+([A-Za-z]+)", text, re.IGNORECASE)
        if loc: data["location"] = loc.group(1).strip()

    return data
