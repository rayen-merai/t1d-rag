from pypdf import PdfReader
text = PdfReader("data/paper.pdf").pages[2].extract_text()
print(text[:800])