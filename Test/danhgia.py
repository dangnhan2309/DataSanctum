from bertopic import BERTopic
from keybert import KeyBERT

print("📌 Bắt đầu chạy chương trình...")

# Đường dẫn đến mô hình đã lưu
model_path = r"D:\model\bertopic_model(ver3-50k_Reference)"

# Tải lại mô hình đã lưu
try:
    topic_model = BERTopic.load(model_path)
    print(f"✅ Mô hình đã được load thành công từ: {model_path}")
except Exception as e:
    print(f"❌ Lỗi khi load mô hình: {e}")
    exit()

# Văn bản mẫu để kiểm tra
sample_text = """
Decision trees are one of the most interpretable models in machine learning,
providing a clear visual representation of the decision-making process. These
models are structured as binary trees, where internal nodes represent tests on
features, branches represent outcomes of these tests, and leaf nodes represent
class labels or predicted values. Decision trees can be used for both
classification and regression tasks. One of their main advantages is their
ability to handle both numerical and categorical data without requiring
extensive preprocessing. However, they are prone to overfitting, especially when
grown to deep levels. To counteract this, techniques like pruning and ensemble
methods such as random forests are commonly applied. This paper presents the
construction, optimization, and limitations of decision trees, followed by  
comparisons with other models on standard datasets.
"""

# Dự đoán chủ đề
predicted_topic, predicted_prob = topic_model.transform([sample_text])

# Kiểm tra kết quả dự đoán
if predicted_topic[0] != -1:
    topic_id = predicted_topic[0]  # ID chủ đề dự đoán
    topic_words = topic_model.get_topic(topic_id)  # Lấy danh sách từ quan trọng trong chủ đề
    topic_words_list = [word for word, _ in topic_words[:20]]  # Lấy 20 từ đại diện

    print(f"\n🔹 Chủ đề dự đoán: {topic_id}")
    print(f"📌 Độ tin cậy: {predicted_prob[0].max():.4f}")
    print(f"🔹 Từ khóa chủ đề: {', '.join(topic_words_list)}")

else:
    print("❌ Không thể xác định chủ đề phù hợp cho văn bản này.")
    exit()

# ------------------------------------------------------------------------------------
# # Phân tích tên chủ đề bằng KeyBERT + spaCy
# nlp = spacy.load("en_core_web_sm")
# kw_model = KeyBERT(model='all-MiniLM-L6-v2')

# def generate_topic_keybert_spacy(topic_words):
#     text = ' '.join(topic_words)
#     keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 3), stop_words='english', top_n=2)
#     return ", ".join([kw[0].title() for kw in keywords])

# # Tạo tên chủ đề từ danh sách từ
# kb_name = generate_topic_keybert_spacy(topic_words_list)

# # In kết quả cuối cùng
# print("-" * 100)
# print("{:<60} | {:<30}".format("TOPIC WORDS", "KEYBERT+spaCy"))
# print("-" * 100)
# print("{:<60} | {:<30}".format(", ".join(topic_words_list), kb_name))
# print("-" * 100)