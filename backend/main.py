# import os
# import pandas as pd
# from src.extract_text import extract_text_based_fields
# from src.extract_form import extract_form_based_fields
# from src.merge_records import merge_by_candidate

# INPUT_DIR = "pdfs"
# OUTPUT_DIR = "output"
# os.makedirs(OUTPUT_DIR, exist_ok=True)

# records = []
# if os.path.exists(INPUT_DIR):
#     for filename in os.listdir(INPUT_DIR):
#         if not filename.lower().endswith(".pdf"): continue
#         pdf_path = os.path.join(INPUT_DIR, filename)
#         fname = filename.lower()
        
#         if "bank" in fname or "personal" in fname:
#             rec = extract_form_based_fields(pdf_path)
#         else:
#             rec = extract_text_based_fields(pdf_path)
            
#         rec["source"] = filename
#         records.append(rec)

#     df = pd.DataFrame(merge_by_candidate(records))
#     df.to_csv(os.path.join(OUTPUT_DIR, "output.csv"), index=False)
#     print("Done.")
# else:
#     print(f"Directory {INPUT_DIR} not found.")


from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import tempfile
from typing import List

# Import your modules
from src.extract_text import extract_text_based_fields
from src.extract_form import extract_form_based_fields
from src.merge_records import merge_by_candidate

app = FastAPI()

# Allow React (running on localhost:5173) to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, change this to your frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def process_pdfs(files: List[UploadFile] = File(...)):
    records = []
    
    # Create a temp folder for this specific request
    with tempfile.TemporaryDirectory() as temp_dir:
        for file in files:
            temp_path = os.path.join(temp_dir, file.filename)
            
            # Save uploaded file temporarily
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Run your existing logic
            fname = file.filename.lower()
            try:
                if "bank" in fname or "personal" in fname:
                    rec = extract_form_based_fields(temp_path)
                else:
                    rec = extract_text_based_fields(temp_path)
                
                rec["source_file"] = file.filename
                records.append(rec)
            except Exception as e:
                print(f"Skipping {file.filename}: {e}")

    # Merge and return JSON
    if records:
        merged = merge_by_candidate(records)
        def sort_key(r):
            cid = str(r.get("candidate_id", ""))
            return (0, int(cid)) if cid.isdigit() else (1, cid)

        merged = sorted(merged, key=sort_key)
        return {"status": "success", "data": merged}
    else:
        return {"status": "error", "message": "No data found"}
