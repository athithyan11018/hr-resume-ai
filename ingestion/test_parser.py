from pdf_parser import extract_text_from_pdf


pdf_path = "data/resumes/test_resume.pdf"

text = extract_text_from_pdf(pdf_path)

print("=" * 60)
print("EXTRACTED RESUME TEXT")
print("=" * 60)

print(text)