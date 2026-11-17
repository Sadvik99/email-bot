import csv

with open("jobs.csv") as f:
    jobs = list(csv.DictReader(f))

for job in jobs:
    with open(job["jd_file"]) as jd:
        job["description"] = jd.read()

    print(f"{job['role']} at {job['company']}")
    print(f"  Send to: {job['contact_name']} <{job['contact_email']}>")
    print(f"  JD length: {len(job['description'])} characters\n")