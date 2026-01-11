def merge_by_candidate(records):
    temp = {}

    # Priority: higher wins when choosing conflicting fields
    DOC_PRIORITY = {
        "resume": 4,
        "text": 2,     # offer/nda/acceptance usually land here
        "form": 1,
        "aadhar": 0,
    }

    def prio(rec):
        return DOC_PRIORITY.get(rec.get("doc_type"), 1)

    for record in records:
        email = record.get("email")
        if not email:
            continue

        if email not in temp:
            temp[email] = {
                "_prio_full_name": -1,
                "_prio_role": -1,
                "_prio_location": -1,
                "_prio_doj": -1,
            }

        for k, v in record.items():
            if v is None or v == "":
                continue

            # Prefer numeric candidate_id (from a real Candidate ID), otherwise keep existing
            if k == "candidate_id":
                curr = str(temp[email].get("candidate_id", ""))
                nv = str(v)
                if nv.isdigit():
                    temp[email]["candidate_id"] = nv
                elif "candidate_id" not in temp[email]:
                    temp[email]["candidate_id"] = nv
                continue

            # Always overwrite these with the latest extracted value
            if k in ["bank_name", "account_number", "aadhar_number", "t_shirt_size", "reporting_manager"]:
                temp[email][k] = v
                continue

            # Full name: choose best source (resume/text > aadhar/form)
            if k == "full_name":
                p = prio(record)
                if p >= temp[email]["_prio_full_name"]:
                    temp[email]["full_name"] = v
                    temp[email]["_prio_full_name"] = p
                continue

            # Role/location/doj also should not be polluted by “... Location/Email”
            if k in ["role", "location", "date_of_joining"]:
                p = prio(record)
                key_prio = "_prio_" + ("doj" if k == "date_of_joining" else k)
                if p >= temp[email][key_prio]:
                    temp[email][k] = v
                    temp[email][key_prio] = p
                continue

            # Default: fill only if empty
            if k not in temp[email] or temp[email][k] in ("", None):
                temp[email][k] = v

    # cleanup
    out = []
    for r in temp.values():
        r.pop("_prio_full_name", None)
        r.pop("_prio_role", None)
        r.pop("_prio_location", None)
        r.pop("_prio_doj", None)
        out.append(r)

    return out

