import datetime
import re
from docx import Document

MONTHS = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
    "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
    "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
}

def parse_week_marker(line, current_year, last_month):
    """
    Convert 'Mar 14' into '# Week of YYYY-MM-DD'.
    Auto-decrement year if month rolls backward (Dec -> Jan).
    """
    parts = line.strip().split()
    if len(parts) == 2 and parts[0] in MONTHS and parts[1].isdigit():
        month = MONTHS[parts[0]]
        day = int(parts[1])

        # Detect rollover: if the new month is greater than last_month, decrement year
        if last_month is not None and month > last_month:
            current_year -= 1

        date = datetime.date(current_year, month, day)
        return f"# Week of {date.isoformat()}", current_year, month
    return None, current_year, last_month

def transform_docx(input_docx, output_txt, start_year=2026):
    doc = Document(input_docx)

    output_lines = []
    current_year = start_year
    last_month = None

    for para in doc.paragraphs:
        line = para.text.strip()
        if not line:
            continue

        # Week markers
        week_header, current_year, last_month = parse_week_marker(line, current_year, last_month)
        if week_header:
            output_lines.append(week_header)
            continue

        # Extract only links from the line
        urls = re.findall(r"https?://\S+", line)
        for url in urls:
            output_lines.append(url)

    with open(output_txt, "w") as f:
        f.write("\n".join(output_lines))

if __name__ == "__main__":
    transform_docx("InterestingPaperCollection-2025.docx", "papers.txt", start_year=2026)

