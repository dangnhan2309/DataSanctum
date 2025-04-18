import os
import json
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from umap import UMAP
from hdbscan import HDBSCAN
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk

# Tải tài nguyên NLTK
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')

# ==== Đường dẫn & cấu hình ====
json_file = r"D:\DataSanctum\model\Dataset\abstracts_80k_from_2020.json"
save_dir = r"D:/model"
model_path = os.path.join(save_dir, "bertopic_model(ver1-50k_Reference)")

if not os.path.exists(save_dir):
    os.makedirs(save_dir)
    print(f"✅ Tạo thư mục: {save_dir}")

# ==== Đọc dữ liệu ====
with open(json_file, "r", encoding="utf-8") as file:
    abstracts = json.load(file)

# Lấy 10.000 mẫu (có thể điều chỉnh)
abstracts = abstracts[:50000]
print(f"📌 Số lượng abstracts thu thập được: {len(abstracts)}")

# ==== Tiền xử lý dữ liệu ====
stop_words = set(stopwords.words('english')) | {'http', 'https', 'amp', 'com'}
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    tokens = [lemmatizer.lemmatize(w) for w in tokens if w.isalnum() and w not in stop_words]
    return ' '.join(tokens)

abstracts = [preprocess_text(a) for a in abstracts]

# ==== Cấu hình mô hình ====
embedding_model = SentenceTransformer('all-mpnet-base-v2')

umap_model = UMAP(n_neighbors=30, min_dist=0.1, metric='cosine')  # tăng n_neighbors
hdbscan_model = HDBSCAN(min_cluster_size=50, min_samples=15, prediction_data=True)


vectorizer_model = CountVectorizer(ngram_range=(1, 2), stop_words='english')  # giảm n-gram

# ==== Huấn luyện BERTopic ====
topic_model = BERTopic(
    embedding_model=embedding_model,
    umap_model=umap_model,
    hdbscan_model=hdbscan_model,
    vectorizer_model=vectorizer_model,
    language='english',
    verbose=True
)

topics, probs = topic_model.fit_transform(abstracts)

# ==== Lưu mô hình ====
try:
    topic_model.save(model_path, save_embedding_model=True)
    print(f"✅ Mô hình đã được lưu tại: {model_path}")
except Exception as e:
    print(f"❌ Lỗi khi lưu mô hình: {e}")

# ==== Kiểm tra load lại ====
try:
    loaded_model = BERTopic.load(model_path)
    print(f"✅ Mô hình đã được load lại từ: {model_path}")
except Exception as e:
    print(f"❌ Lỗi khi load mô hình: {e}")

# ==== Kiểm tra kết quả ====
print(topic_model.get_topic_info().head())
