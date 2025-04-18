import magic

class FileProcessor:
    def __init__(self):
        self.extractor_map = {
            'application/pdf': 'pdf_extractor',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'word_extractor',
            'text/plain': 'text_extractor',
            'text/csv': 'csv_extractor',
            'application/json': 'json_extractor',
            'image/jpeg': 'image_extractor',
            'image/png': 'image_extractor',
            # Thêm các loại ảnh khác nếu cần
        }
        self.mime_detector = magic.Magic(mime=True)  # Khởi tạo đối tượng Magic để xác định MIME type

    def process_file(self, file_path):
        mime_type = self.mime_detector.from_file(file_path)  # Sử dụng magic để xác định MIME type
        if not mime_type:
            print(f"⚠️ Không xác định được MIME type cho file: {file_path}")
            return None, None

        extractor_func_name = self.extractor_map.get(mime_type)
        if not extractor_func_name:
            print(f"⚠ Không hỗ trợ extractor cho MIME type: {mime_type}")
            return mime_type, None

        return mime_type, extractor_func_name
    def main():
        file_path = input("Nhập đường dẫn tệp cần xử lý: ")
        processor = FileProcessor()
        mime, extractor = processor.process_file(file_path)

        if mime:
            print(f"✔ MIME type: {mime}")
            if extractor:
                print(f"✔ Sử dụng hàm extractor: {extractor}")
            else:
                print("⚠ Không tìm thấy hàm extractor phù hợp.")
        else:
            print("❌ Không thể xử lý tệp.")

if __name__ == "__main__":
    main()