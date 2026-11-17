import csv
from sentence_transformers import SentenceTransformer, util

# --- Load jobs (Step 1) ---
with open("jobs.csv") as f:
    jobs = list(csv.DictReader(f))
for job in jobs:
    with open(job["jd_file"]) as jd:
        job["description"] = jd.read()

# --- Load resume bullets (Step 2) ---
chunks, heading = [], ""
with open("resume.txt") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        if line.startswith("-"):
            chunks.append(f"{heading}: {line.lstrip('- ').strip()}")
        else:
            heading = line

# --- Step 3: turn text into embeddings and compare ---
model = SentenceTransformer("all-MiniLM-L6-v2")
bullet_vecs = model.encode(chunks)

for job in jobs:
    # each meaningful line of the job description
    jd_lines = [l.strip() for l in job["description"].splitlines() if len(l.strip()) > 20]
    jd_vecs = model.encode(jd_lines)

    # score every bullet against every JD line, keep each bullet's best match
    scores = util.cos_sim(bullet_vecs, jd_vecs).max(dim=1).values
    top3 = scores.argsort(descending=True)[:3]

    print(f"\n=== {job['role']} at {job['company']} ===")
    for i in top3:
        print(f"  {scores[i]:.2f}  {chunks[int(i)]}")
