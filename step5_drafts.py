import os
import re
import time
import imaplib
from email.message import EmailMessage
import csv
import anthropic
from sentence_transformers import SentenceTransformer, util

MIN_FIT = 6        # skip jobs the AI rates below this (1-10)
DRY_RUN = False    # True = only print ratings, don't write emails or drafts

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
    sim = util.cos_sim(bullet_vecs, model.encode(jd_lines))  # rows = bullets, columns = JD lines

    # pick the 3 bullets that best fit the job (same as before)
    bullet_scores = sim.max(dim=1).values
    order = bullet_scores.argsort(descending=True)[:n]
    bullets = [chunks[int(i)] for i in order]

    # NEW fit score: how much of the job the resume covers
    fit = float(sim.max(dim=0).values.mean())
    return bullets, fit

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

def rate_fit(job):
    resume_text = "\n".join(f"- {c}" for c in chunks)
    prompt = f"""Rate how well this candidate fits the job, from 1 to 10.
10 = meets nearly all core requirements
5 = related field, but missing key required skills
1 = a different field entirely

Compare the job's required skills to the resume. Don't judge by job title alone.

Job: {job['role']} at {job['company']}
{job['description']}

Resume:
{resume_text}

Reply with only the number."""

    response = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(b.text for b in response.content if b.type == "text")
    number = re.search(r"\d+", text)
    return int(number.group()) if number else 0

# --- NEW: Step 5, save as Gmail draft with resume attached ---
GMAIL_ADDRESS = os.environ.get("GMAIL_ADDRESS", "msadvikreddy@gmail.com")

def save_draft(job, email_text):
    first_line, body = email_text.split("\n", 1)
    subject = first_line.replace("Subject:", "").strip()

    msg = EmailMessage()
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = job["contact_email"]
    msg["Subject"] = subject
    msg.set_content(body.strip())

    with open("resume.pdf", "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="pdf",
            filename="Sadvik_Reddy_Mandadapu_Resume.pdf",
        )

    with imaplib.IMAP4_SSL("imap.gmail.com") as gmail:
        gmail.login(GMAIL_ADDRESS, os.environ["GMAIL_APP_PASSWORD"])
        gmail.append("[Gmail]/Drafts", "\\Draft",
                     imaplib.Time2Internaldate(time.time()), msg.as_bytes())

for job in jobs:
    bullets, coverage = top_bullets(job["description"])
    fit = rate_fit(job)
    if fit == 0:
        print(f"Couldn't read a rating for {job['role']} at {job['company']} - check rate_fit")
        continue
    label = f"{job['role']} at {job['company']}"

    if fit < MIN_FIT:
        print(f"Skipped (fit {fit}/10): {label}")
        continue

    if DRY_RUN:
        print(f"Would draft (fit {fit}/10): {label}")
        continue

    email_text = write_email(job, bullets)
    save_draft(job, email_text)
    print(f"Draft saved (fit {fit}/10): {label} -> {job['contact_email']}")
