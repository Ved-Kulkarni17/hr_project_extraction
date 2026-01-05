def merge_by_candidate(records):
    merged = {}
    temp = {}

    for record in records:
        email = record.get("email")
        if not email: continue

        if email not in temp: temp[email] = {}

        for k, v in record.items():
            if v and v != "":
                # Prioritize Numeric ID
                if k == "candidate_id":
                    curr = temp[email].get("candidate_id", "")
                    if v.isdigit() and not str(curr).isdigit():
                        temp[email][k] = v
                    elif "candidate_id" not in temp[email]:
                        temp[email][k] = v
                else:
                    if k not in temp[email] or temp[email][k] in ("", None):
                        temp[email][k] = v
                    # Always overwrite with masked/specific values
                    if k in ["bank_name", "account_number", "aadhar_number", "t_shirt_size", "reporting_manager"]:
                        temp[email][k] = v

    return list(temp.values())
