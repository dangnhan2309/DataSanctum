from bertopic import BERTopic

# Đường dẫn đến mô hình đã lưu
model_path = r"D:\model\bertopic_model(ver2-50k_Reference)"

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
    topic_name = ", ".join([word for word, _ in topic_words[:20]])  # Lấy 5 từ đại diện cho chủ đề
        
    print(f"\n🔹 Chủ đề dự đoán: {topic_id}")
    print(type(predicted_prob[0]))
    print(predicted_prob[0])

    max_prob = predicted_prob.max()
    print(f"📌 Độ tin cậy: {max_prob:.4f}")
    print(f"🔹 Tên chủ đề: {topic_name}")
else:
    print("❌ Không thể xác định chủ đề phù hợp cho văn bản này.")
