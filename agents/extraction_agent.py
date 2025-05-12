from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_path):
    """Extracts and returns text from a given PDF file."""
    try:
        text = ""
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""
