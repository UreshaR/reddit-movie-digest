"""
Reads movie_digest.json (produced by summarize_movies.py) and generates a
clean, readable PDF report: film name + description + source link per post.

Run this AFTER summarize_movies.py.
"""

import json
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable
)

INPUT_FILE = "movie_digest.json"
OUTPUT_FILE = "movie_digest.pdf"


def build_pdf():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        digest = json.load(f)

    doc = SimpleDocTemplate(
        OUTPUT_FILE,
        pagesize=letter,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DigestTitle", parent=styles["Title"], fontSize=20, spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "DigestSubtitle", parent=styles["Normal"], fontSize=10,
        textColor=colors.grey, spaceAfter=20,
    )
    film_style = ParagraphStyle(
        "FilmName", parent=styles["Heading2"], fontSize=14,
        textColor=colors.HexColor("#1a1a2e"), spaceBefore=14, spaceAfter=4,
    )
    desc_style = ParagraphStyle(
        "Description", parent=styles["Normal"], fontSize=10.5,
        leading=15, spaceAfter=4,
    )
    link_style = ParagraphStyle(
        "SourceLink", parent=styles["Normal"], fontSize=8.5,
        textColor=colors.HexColor("#4a4a6a"), spaceAfter=2,
    )

    story = []
    story.append(Paragraph("r/movies Digest", title_style))
    story.append(Paragraph(
        f"Generated {datetime.now().strftime('%B %d, %Y %H:%M')} "
        f"&middot; last 2 days &middot; {len(digest)} posts analyzed",
        subtitle_style,
    ))
    story.append(HRFlowable(width="100%", color=colors.HexColor("#cccccc")))

    shown = 0
    for entry in digest:
        if entry["film"] == "N/A" or not entry.get("description"):
            continue

        shown += 1
        story.append(Paragraph(entry["film"], film_style))
        story.append(Paragraph(entry["description"], desc_style))
        story.append(Paragraph(
            f'Source: <link href="{entry["url"]}">{entry["url"]}</link>',
            link_style,
        ))
        story.append(Spacer(1, 6))

    if shown == 0:
        story.append(Paragraph(
            "No identifiable films found in this period.", desc_style
        ))

    doc.build(story)
    print(f"Saved {OUTPUT_FILE} ({shown} films listed)")


if __name__ == "__main__":
    build_pdf()