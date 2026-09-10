from pathlib import Path
import json

from pdf_parser import extract_text_from_pdf


RESUME_DIR = Path("data/resumes")
OUTPUT_DIR = Path("data/processed")


def ingest_resumes():
    """Extract text from all PDF resumes and save them as JSON."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    pdf_files = list(RESUME_DIR.glob("*.pdf"))

    print(f"Found {len(pdf_files)} PDF resumes.")

    for pdf_path in pdf_files:

        print(f"Processing: {pdf_path.name}")

        text = extract_text_from_pdf(str(pdf_path))

        resume_data = {
            "resume_id": pdf_path.stem,
            "filename": pdf_path.name,
            "text": text,
        }

        output_path = OUTPUT_DIR / f"{pdf_path.stem}.json"

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(resume_data, file, indent=4, ensure_ascii=False)

        print(f"Saved: {output_path}")


if __name__ == "__main__":
    ingest_resumes()