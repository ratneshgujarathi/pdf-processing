import PyPDF2

def process_pdf(file):
    reader = PyPDF2.PdfFileReader(file)
    text = ""
    for page_num in range(reader.numPages):
        text += reader.getPage(page_num).extract_text()
    
    return {"text": text, "page_count": reader.numPages}
