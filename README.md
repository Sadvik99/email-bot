# Job Application Email Bot (a RAG learning project)

**Status: work in progress.** This is not a finished tool. I built it to learn how RAG works and how to put it into practice.

## Why I built it

I wanted to understand RAG (Retrieval-Augmented Generation) by building something real. Writing cold emails for job applications seemed like a good test case. Each email needs to match a different job, and that is exactly the kind of problem RAG is meant to solve.

## What it does

You give it a job description and the hiring person's email. The bot then:

1. **Checks if the job is a good fit.** The AI reads the job and my resume and gives a score from 1 to 10. If the score is below 6, the bot skips the job.
2. **Finds my best experience for the job.** It picks the 3 lines from my resume that match the job most closely.
3. **Writes the email.** The AI writes the email using only those 3 lines, so it can't make up skills I don't have.
4. **Saves a Gmail draft.** The email goes into my Drafts folder with my resume attached. Nothing gets sent until I send it.

Steps 2 and 3 are the RAG part. First you find the right information. Then you give it to the AI to write with.

## Being honest: it's not faster yet

Right now, using this bot takes me **longer** than writing a cold email myself.

For each job, I have to:
- Copy the job description into a text file
- Add the company, role, and contact to a spreadsheet
- Set my keys in the terminal
- Run the script, then open Gmail and review the draft

When I write an email by hand, I just open Gmail and type. So the bot works, but it doesn't save time yet. The setup work for each job costs more time than the writing it saves.

## What I learned

**RAG works.** The emails used my real experience and matched each job well.

**Comparing words wasn't enough to judge fit.** At first, I checked fit by comparing how similar the job's wording was to my resume. A good job and a bad job got almost the same score, only 0.02 apart. When I asked the AI to judge the fit instead, the scores were 9 and 5, a clear difference.

**My takeaway:** comparing words is good for *finding* the right resume lines. The AI is better at *deciding* whether a job is worth applying to.

## What needs to improve for real use

To make this faster than writing by hand, it needs:

- **Paste a job link instead of a text file.** The bot should read the job posting from the URL by itself.
- **No spreadsheet.** Enter the company, role, and contact in one simple prompt or form.
- **A simple web page.** Paste the job, click a button, and see the email. No terminal needed.
- **Save keys once.** Keep them in a settings file so I don't set them every time.
- **Read my resume from the PDF.** Then I don't have to keep a separate text copy.
- **Batch mode.** Do 10 jobs in one go, so the setup time pays off.

## Files

- `step1_jobs.py`: reads my list of jobs and contacts
- `step2_resume.py`: splits my resume into separate lines
- `step3_match.py`: finds the resume lines that match each job
- `step4_write.py`: has the AI write the email
- `step5_drafts.py`: runs everything and saves the Gmail drafts

## What I used

- Python
- sentence-transformers, to match resume lines to jobs (runs free on my laptop)
- Claude API, to score fit and write the emails
- Gmail, to save the drafts

## How to try it

1. Install the libraries:
   ```
   python -m pip install sentence-transformers anthropic
   ```

2. Add your files to the folder:
   - `resume.txt`: your resume as plain text. Put the company on one line, then each bullet on its own line starting with `-`.
   - `resume.pdf`: the resume you want to attach.
   - `jobs.csv`: one row per job, with the company, role, contact name, contact email, and job description file.
   - `jds/`: a folder with one text file for each job description.

3. Set your keys in the terminal. Don't put them in your code.
   ```
   export ANTHROPIC_API_KEY="your-claude-key"
   export GMAIL_ADDRESS="you@gmail.com"
   export GMAIL_APP_PASSWORD="your-gmail-app-password"
   ```
   You can make a Gmail App Password at https://myaccount.google.com/apppasswords

4. Do a test run first. In `step5_drafts.py`, set `DRY_RUN = True`. Then run:
   ```
   python step5_drafts.py
   ```
   This only shows the fit scores. It doesn't make any drafts.

5. When the scores look right, change it to `DRY_RUN = False` and run it again. Then check your Gmail Drafts.

## Why it doesn't send emails by itself

I want to read every email before it goes out. A wrong name or a bad email address to a hiring manager is hard to undo. Sending lots of emails automatically can also get your Gmail marked as spam. So the bot only makes drafts.
