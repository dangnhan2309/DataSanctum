import os
import PyPDF2
import csv
import json
import magic
from PIL import Image
import docx
import pytesseract
from pdf2image import convert_from_path

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class Extractor:
    def __init__(self):
        pass
    def ocr_image_extractor(self, file_path):
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image, lang='eng+vie')  # Hỗ trợ cả tiếng Việt
        return text or "Không phát hiện được văn bản từ ảnh"

    # OCR from PDF scan (dạng ảnh)
    def ocr_pdf_extractor(self, file_path):
        try:
            images = convert_from_path(file_path)
            text = ""
            for i, image in enumerate(images):
                page_text = pytesseract.image_to_string(image, lang='eng+vie')
                text += f"--- Trang {i+1} ---\n" + page_text + "\n"
            return text or "Không phát hiện văn bản trong PDF scan"
        except Exception as e:
            return f"Lỗi OCR PDF: {str(e)}"
        
    def text_extractor(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def pdf_extractor(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted
                return text or "Không có nội dung trong file PDF"
        except Exception as e:
            return f"Lỗi khi đọc file PDF: {str(e)}"

    def word_extractor(self, file_path):
        doc = docx.Document(file_path)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text

    def csv_extractor(self, file_path):
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            text = ""
            for row in reader:
                text += ', '.join(row) + "\n"
            return text

    def json_extractor(self, file_path):
        with open(file_path, mode='r', encoding='utf-8') as f:
            data = json.load(f)
            return json.dumps(data, indent=4)

    def image_extractor(self, file_path):
        image = Image.open(file_path)
        image.show()
        return "Image extracted and shown"

    @staticmethod
    def detect_mime_type(file_path):
        mime = magic.Magic(mime=True)
        return mime.from_file(file_path)

    @staticmethod
    def truncate_text(text, max_length=10000):
        return text if len(text) <= max_length else text[:max_length] + "\n... (truncated)"

    def get_extractor_by_mime_type(self, mime_type):
        if 'text/plain' in mime_type:
            return self.text_extractor
        elif 'application/pdf' in mime_type:
            return self.pdf_extractor
        elif 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in mime_type:
            return self.word_extractor
        elif 'text/csv' in mime_type:
            return self.csv_extractor
        elif 'application/json' in mime_type:
            return self.json_extractor
        elif 'image' in mime_type:
            return self.image_extractor
        else:
            return None

# Main function to test the extractor
def main():
    file_path = r"D:\DST\support\Tool\material\O.docx"

    if not os.path.exists(file_path):
        print(f"❌ File không tồn tại: {file_path}")
        return

    extractor = Extractor()
    mime_type = Extractor.detect_mime_type(file_path)
    print(f"MIME Type: {mime_type}")

    extractor_func = extractor.get_extractor_by_mime_type(mime_type)
    if extractor_func:
        result = extractor_func(file_path)
        print(Extractor.truncate_text(result))  # Giới hạn độ dài hiển thị
    else:
        print(f"⚠ Loại file không được hỗ trợ: {mime_type}")

if __name__ == "__main__":
    main()
