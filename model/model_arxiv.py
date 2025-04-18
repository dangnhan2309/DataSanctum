import os
import json
from datetime import datetime

# File NDJSON đầu vào
jsonl_file = "D:/arxiv-metadata-oai-snapshot.json"

# Thư mục và file output
save_dir = "D:/DataSanctum/Model/Dataset"
output_file = os.path.join(save_dir, "abstracts_80k_from_2020.json")

# Tạo thư mục nếu chưa có
if not os.path.exists(save_dir):
    os.makedirs(save_dir)
    print(f"✅ Tạo thư mục: {save_dir}")

abstracts = []

# Đọc từng dòng NDJSON
with open(jsonl_file, "r", encoding="utf-8") as f:
    for line in f:
        try:
            data = json.loads(line)
            # Lấy ngày tạo từ versions[0]['created']
            created_str = data.get("versions", [{}])[0].get("created", "")
            if created_str:
                created_date = datetime.strptime(created_str, "%a, %d %b %Y %H:%M:%S %Z")
                if created_date.year >= 2020:
                    abstract = data.get("abstract", "").strip()
                    if abstract:
                        abstracts.append(abstract)

            if len(abstracts) >= 80000:
                break

        except (json.JSONDecodeError, ValueError):
            continue  # Bỏ qua dòng lỗi

# Ghi ra file JSON (chỉ chứa danh sách abstracts)
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(abstracts, f, ensure_ascii=False, indent=2)

print(f"📦 Đã lưu {len(abstracts)} abstracts vào:\n{output_file}")
