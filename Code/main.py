from bertopic import BERTopic
from keybert import KeyBERT
from extractors import Extractor
from fileprocessor import FileProcessor
from nltk.corpus import stopwords
import re

# 1. Load mô hình BERTopic đã lưu
def load_topic_model(model_path):
    try:
        model = BERTopic.load(model_path)
        print(f"✅ Đã load BERTopic model từ: {model_path}")
        return model
    except Exception as e:
        import traceback
        print("❌ Lỗi khi load model:")
        traceback.print_exc()  # In toàn bộ stack trace
        return None

# 2. Xác định loại file và hàm extractor
def detect_file_type_and_extractor(file_path, file_processor):
    result = file_processor.process_file(file_path)
    if result is None:
        print("❌ Không thể xử lý file. Dừng pipeline.")
        return None
    mime_type, extractor_func_name = result
    print(f"[ℹ] MIME Type: {mime_type}")
    print(f"[ℹ] Extractor: {extractor_func_name}")
    
    if mime_type not in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/pdf']:
        print("⚠ Không xác định MIME type hợp lệ.")
        return None
    
    return extractor_func_name

# 3. Làm sạch văn bản
def clean_text_remove_stopwords(text):
    stop_words = set(stopwords.words('english') + ['http', 'https', 'amp', 'com'])
    words = re.findall(r'\b\w+\b', text.lower())
    filtered = [word for word in words if word not in stop_words]
    return ' '.join(filtered)

# 4. Trích xuất văn bản từ file
def extract_text(file_path, extractor_func_name, extractor):
    extractor_func = getattr(extractor, extractor_func_name, None)
    if extractor_func:
        text = extractor_func(file_path)
        print(f"📑 Đã trích xuất {len(text)} ký tự từ file.")
        cleaned_text = clean_text_remove_stopwords(text)
        print(f"✅ Văn bản sau khi loại bỏ stopwords: {len(cleaned_text)} ký tự.")
        return cleaned_text
    else:
        print(f"⚠ Không tìm thấy hàm extractor: {extractor_func_name}")
        return None

# 5. Dự đoán chủ đề
def predict_topic(text, topic_model):
    topics, probs = topic_model.transform([text])
    if topics[0] == -1:
        print("⚠ Không xác định được chủ đề.")
        return None
    topic_id = topics[0]
    topic_words = topic_model.get_topic(topic_id)
    topic_words_list = [word for word, _ in topic_words[:15]]
    confidence = probs[0].max()
    return topic_id, topic_words_list, confidence

# 6. Tạo tên chủ đề
def generate_topic_name(topic_words):
    kw_model = KeyBERT(model="all-MiniLM-L6-v2")
    text = " ".join(topic_words)
    keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 3), stop_words='english', top_n=1)
    return keywords[0][0].title() if keywords else "Unnamed Topic"

# 7. Hiển thị thông tin chủ đề
def display_topic_info(topic_id, topic_words, confidence, topic_name):
    print("\n🎯 Chủ đề dự đoán")
    print("-" * 50)
    print(f"🆔 ID: {topic_id}")
    print(f"🔍 Tên: {topic_name}")
    print(f"💡 Từ khóa: {', '.join(topic_words)}")
    print(f"📈 Độ tin cậy: {confidence:.4f}")
    print("-" * 50)

# 8. Pipeline chính
def process_file_for_topic(file_path, model_path):
    topic_model = load_topic_model(model_path)
    if not topic_model:
        return

    file_processor = FileProcessor()
    extractor = Extractor()

    extractor_func_name = detect_file_type_and_extractor(file_path, file_processor)
    if not extractor_func_name:
        return

    text = extract_text(file_path, extractor_func_name, extractor)
    if not text:
        print("❌ Không có văn bản để phân tích.")
        return

    result = predict_topic(text, topic_model)
    if not result:
        return
    topic_id, topic_words, confidence = result
    topic_name = generate_topic_name(topic_words)

    display_topic_info(topic_id, topic_words, confidence, topic_name)

# 9. Hàm main
def main():
    file_path = r"D:\DST\support\Tool\material\O.docx"
    model_path = r"D:\model\bertopic_model(ver4-50k_Reference)"
    process_file_for_topic(file_path, model_path)

if __name__ == "__main__":
    main()
