chunks = []
heading = ""

with open("resume.txt") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue                   # skip blank lines
        if line.startswith("-"):
            bullet = line.lstrip("- ").strip()
            chunks.append(f"{heading}: {bullet}")
        else:
            heading = line             # remember which job we're under

print(f"Found {len(chunks)} resume bullets:\n")
for i, chunk in enumerate(chunks):
    print(f"[{i}] {chunk}")
