import csv
import anthropic
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

# --- Match bullets to each job (Step 3) ---
model = SentenceTransformer("all-MiniLM-L6-v2")
bullet_vecs = model.encode(chunks)

def top_bullets(description, n=3):
    jd_lines = [l.strip() for l in description.splitlines() if len(l.strip()) > 20]
    scores = util.cos_sim(bullet_vecs, model.encode(jd_lines)).max(dim=1).values
    return [chunks[int(i)] for i in scores.argsort(descending=True)[:n]]

# --- NEW: Step 4, AI writes the email ---
client = anthropic.Anthropic()

def write_email(job, bullets):
    bullet_text = "\n".join(f"- {b}" for b in bullets)
    prompt = f"""Write a short job application email from Sadvik Reddy Mandadapu.

Recipient: {job['contact_name']}
Role: {job['role']} at {job['company']}

Job description:
{job['description']}

Sadvik's most relevant experience (use ONLY these facts, do not invent anything):
{bullet_text}

Rules:
- Address the recipient by first name
- Under 150 words, friendly and professional, no buzzwords
- Connect 2-3 of the experiences above to what the job needs
- Mention that his resume is attached
- End by asking for a short call
- First line must be "Subject: ..." then a blank line, then the email body"""

    response = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=4000,  # room for the model's thinking plus the email
        messages=[{"role": "user", "content": prompt}],
    )
    # The reply can include a thinking block before the text, so grab the text block
    return next(b.text for b in response.content if b.type == "text").strip()

for job in jobs:
    bullets = top_bullets(job["description"])
    print(f"\n========== {job['role']} at {job['company']} ==========\n")
    print(write_email(job, bullets))
