from bertopic import BERTopic
from fileprocessor import FileProcessor
from extractors import Extractor
from nltk.corpus import stopwords
import re
from keybert import KeyBERT
from transformers import T5Tokenizer, T5ForConditionalGeneration
import spacy 
from transformers import pipeline
import subprocess

def clean_text_remove_stopwords(text):
    stop_words = set(stopwords.words('english') + ['http', 'https', 'amp', 'com'])
    words = re.findall(r'\b\w+\b', text.lower())
    filtered = [word for word in words if word not in stop_words]
    return ' '.join(filtered)

def show_vnaban(filepath, function):
    try:
        print("\U0001F50D Start to extracting ....")
        processor = FileProcessor()
        mime_type, extractor_name = processor.process_file(filepath)
        print("-" * 50)
        print(f"\U0001F4C4 MIME type xác định: {mime_type}")
        print(f"\U0001F6E0️ Hàm extractor tương ứng: {extractor_name}")

        if not extractor_name:
            raise ValueError("⚠ Không có extractor phù hợp cho file này.")

        extractor = Extractor()
        extractor_func = getattr(extractor, extractor_name, None)
        if not extractor_func:
            raise AttributeError(f"❌ Không tìm thấy hàm '{extractor_name}' trong Extractor.")

        result = extractor_func(filepath)

        if function.lower() == "raw" or function.lower() == "show":
            print("\U0001F4E5 Kết quả trích xuất nội dung:")
            print(result[:500])
            return result

        elif function.lower() == "test":
            return result

        elif function.lower() == "cleaned":
            print("\U0001F9F9 Start Cleaning ...")
            after_clean = clean_text_remove_stopwords(result)
            print("✅ Finished Cleaning!")
            print("\U0001F9FE Kết quả sau khi làm sạch:")
            print(after_clean)
            return after_clean

        else:
            raise ValueError(f"⚠ Không hỗ trợ chế độ function: '{function}'")

    except Exception as e:
        print(f"❌ Đã xảy ra lỗi: {e}")
        raise e

    
def load_spacy_model(model_name="en_core_web_sm"):
    try:
        return spacy.load(model_name)
    except OSError:
        print(f"⚠️ spaCy model '{model_name}' chưa có, đang tải xuống...")
        subprocess.run(["python", "-m", "spacy", "download", model_name])
        return spacy.load(model_name)
#khong dung
def extract_first_50_lines(result):
    lines = result.splitlines()  # Chia nội dung thành các dòng
    text_50 = "\n".join(lines[:50])  # Lấy 50 dòng đầu và nối lại thành văn bản
    return text_50

def interactive_menu(filepath, model_path):
    while True:
        print("\n🧪 MENU TEST SHOW_VNABAN 🧪")
        print("1. Hiển thị Raw text (50 dòng đầu)")
        print("2. Hiển thị text sau khi clean stopwords")
        print("3. Hiển thị cả Raw và Cleaned")
        print("4. Testing lỗi model")
        print("0. Thoát")

        choice = input("\n🔢 Chọn chức năng (0-5): ").strip()

        if choice == "1":
            print("\n📜 Hiển thị văn bản gốc:")
            show_vnaban(filepath, "raw")

        elif choice == "2":
            print("\n🧼 Hiển thị văn bản đã được làm sạch:")
            show_vnaban(filepath, "cleaned")

        elif choice == "3":
            print("\n📜 Văn bản gốc:")
            raw_text = show_vnaban(filepath, "raw")
            print("\n🧼 Văn bản sau khi clean:")
            cleaned = clean_text_remove_stopwords(raw_text)
            print(cleaned)

        elif choice == "4":
            text = show_vnaban(filepath, "raw")
            process_file_for_topic(filepath, model_path, text)

        elif choice == "0":
            print("👋 Kết thúc.")
            break

        else:
            print("⚠ Vui lòng chọn một số từ 0 đến 5.")

def model_test(model_path):
    print("50"*50)


def load_model(model_path):
    try:
        model = BERTopic.load(model_path)
        print(f"✅ Đã load BERTopic model từ: {model_path}")
        return model
    except Exception as e:
        import traceback
        print("❌ Lỗi khi load model:")
        traceback.print_exc()  # In toàn bộ stack trace
        return None
def process_file_for_topic(file_path, model_path,text):
    topic_model = load_model(model_path)
    if not topic_model:
        return
    result = predict_topic(text, topic_model)
    if not result:
        return
    topic_id, topic_words, confidence = result
    print(topic_words)

    topic_namet1,topic_namet2,topic_namet3,topic_namespacy,topic_name_tranformer,topic_namekeybert = generate_topic_name(topic_words)

    display_topic_info(topic_id, topic_words, confidence,topic_namet1,topic_namet2,topic_namet3,topic_namespacy,topic_name_tranformer,topic_namekeybert )
    # 5. Dự đoán chủ đề
def predict_topic(text, topic_model):
    topics, probs = topic_model.transform([text])
    print(f"\n📘 Chủ đề dự đoán: {topics[0]}")
    print(f"📈 Xác suất: {probs[0]}")

    if topics[0] == -1:
        print("⚠ Không xác định được chủ đề.")
        return None

    topic_id = topics[0]
    topic_words = topic_model.get_topic(topic_id)
    topic_words_list = [word for word, _ in topic_words[:15]]

    confidence = probs[0].max()
    return topic_id, topic_words_list, confidence


# 6. Tạo tên chủ đề
def generate_topic_name(topic_words_list):
    keywords= topic_words_list
    var1 = generate_topic_t5(keywords, model_name='t5-large')
    var2= generate_topic_t5_small(keywords)
    var3= generate_topic_t5_medium(keywords)
    var4= generate_topic_spacy(keywords)
    var5= generate_topic_transformer_summarizer(keywords)
    var6= generate_topic_keybert(keywords)
    print("\n🧠 Gợi ý tên chủ đề từ các phương pháp:")
    print(f"T5-large: {var1}")
    print(f"T5-small: {var2}")
    print(f"T5-medium: {var3}")
    print(f"SpaCy: {var4}")
    print(f"Transformer (BART): {var5}")
    print(f"KeyBERT: {var6}")
    return var1,var2,var3,var4,var5,var6

def generate_topic_t5(keywords, model_name="t5-large"):
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained(model_name)

    input_text = "summarize: " + ", ".join(keywords)
    input_ids = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)
    summary_ids = model.generate(input_ids, max_length=10, num_beams=4, early_stopping=True)

    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)
def generate_topic_t5_medium(keywords):
    return generate_topic_t5(keywords, model_name="t5-base")  

def generate_topic_t5_small(keywords):
    return generate_topic_t5(keywords, model_name="t5-small")

def generate_topic_keybert(keywords):
    kw_model = KeyBERT()
    joined_text = " ".join(keywords)
    topic = kw_model.extract_keywords(joined_text, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=1)
    return topic[0][0] if topic else "Unknown Topic"  

def generate_topic_spacy(keywords):
    nlp = load_spacy_model("en_core_web_sm")
    doc = nlp(" ".join(keywords))
    chunks = [chunk.text for chunk in doc.noun_chunks]
    return chunks[0] if chunks else "General Topic" 

def generate_topic_transformer_summarizer(keywords):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")  # Or "google/pegasus-xsum"
    input_text = " ".join(keywords)
    result = summarizer(input_text, max_length=10, min_length=3, do_sample=False)
    return result[0]['summary_text']

# 7. Hiển thị thông tin chủ đề
def display_topic_info(topic_id, topic_words, confidence,var1,var2,var3,var4,var5,var6):
    print("\n🎯 Chủ đề dự đoán")
    print("-" * 50)
    print(f"🆔 ID: {topic_id}")
    print(f"🔍 Tên: {var1}")
    print(f"🔍 Tên2: {var2}")
    print(f"🔍 Tên3: {var3}")
    print(f"🔍 Tên4: {var4}")
    print(f"🔍 Tên5: {var5}")
    print(f"🔍 Tên6: {var6}")
    print(f"💡 Từ khóa: {', '.join(topic_words)}")
    print(f"📈 Độ tin cậy: {confidence:.4f}")
    print("-" * 50)
def main():
    filepath = r"D:\test.txt"
    model_path = r"D:\model\bertopic_model(ver1-50k_Reference)"
    interactive_menu(filepath,model_path)
    # topic_model = BERTopic.load(model_path)
    # topics = topic_model.get_topics()
    # print(f"Số lượng chủ đề được tìm ra: {len(topics)}")

if __name__ == "__main__":
    main()
