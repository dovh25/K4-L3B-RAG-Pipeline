# RAG evaluation results

## Run information

| Field                              | Value |
| ---------------------------------- | ----- |
| Evaluation date                    | 2026-09-25 |
| Framework and version              | Ragas 0.4.3, Pytest 7.4.4 |
| Evaluator model                    | Gemini (google-genai) |
| Generator model                    | gemini-3.5-flash |
| Embedding model                    | BAAI/bge-m3 & text-embedding-004 (dim 1024) |
| Corpus version/commit              | Legal (3 docs) + News (5 articles) - 8 documents standardized |
| Golden dataset size                | 15 grounded Q&A pairs |
| `top_k`                            | 5 |
| Fallback threshold and calibration | 0.35 (calibrated with in-domain and out-of-domain queries) |

## Configurations

- **Config A — dense-only:** Sử dụng ChromaDB semantic vector search với Cosine similarity, không áp dụng BM25 hay Reranking.
- **Config B — hybrid + RRF:** Kết hợp đồng thời ChromaDB dense search và BM25 lexical search trên cùng tập chunks, gộp bảng xếp hạng bằng Reciprocal Rank Fusion (k=60), có fallback PageIndex khi dense score < 0.35.

Hai config sử dụng chung toàn bộ golden dataset (15 câu hỏi), generator model (Gemini), evaluator prompt và top_k=5; chỉ thay đổi chiến lược retrieval.

## Overall scores

| Metric            | Config A | Config B | Delta B−A |
| ----------------- | -------: | -------: | --------: |
| Faithfulness      |     0.84 |     0.93 |     +0.09 |
| Answer relevance  |     0.81 |     0.90 |     +0.09 |
| Context recall    |     0.78 |     0.92 |     +0.14 |
| Context precision |     0.79 |     0.91 |     +0.12 |
| **Average**       |     0.805|     0.915|     +0.110|

## A/B comparison

- **Cấu hình tốt hơn:** Config B (Hybrid + RRF) vượt trội rõ rệt trên tất cả 4 chỉ số đo lường.
- **Evidence:**
  - Nhờ có BM25, hệ thống tìm chính xác các thực thể định danh, số hiệu văn bản luật (như "Nghị định 01/2021", "Thông tư 40/2021", "mẫu S1-HKD", "ngưỡng 100 triệu đồng") mà Dense retrieval đơn thuần đôi khi bị phân tán sự chú ý do khoảng cách cosine.
  - Context Recall tăng mạnh từ 0.78 lên 0.92 (+14%) nhờ RRF kéo được các chunks chứa điều khoản cụ thể lên top 5.
  - Faithfulness tăng từ 0.84 lên 0.93 (+9%) do context được sắp xếp (reorder) và chứa chính xác điều luật gốc, giúp mô hình hạn chế tối đa suy diễn ngoài văn bản.
- **Trade-off về latency/cost:**
  - Latency trung bình: Config A mất ~450ms; Config B mất ~650ms (tăng ~200ms do tính toán BM25 và hợp nhất RRF).
  - Chi phí: Không tăng thêm chi phí API bên ngoài do BM25 và RRF chạy hoàn toàn trên CPU local. Mức đánh đổi 200ms độ trễ để đổi lấy 11% chất lượng là hoàn toàn xứng đáng trong bài toán tra cứu pháp luật.

## Worst performers

|   # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage             | Root cause |
| --: | -------- | ------ | -----------: | --------: | -----: | --------: | ------------------------- | ---------- |
|   1 | Hộ kinh doanh nộp thuế theo phương pháp kê khai phải lập bao nhiêu loại sổ kế toán theo Thông tư 88? | Config A | 0.70 | 0.75 | 0.60 | 0.65 | retrieval | Dense search chỉ lấy được đoạn trích dẫn khái quát về chế độ kế toán mà bỏ sót danh sách chi tiết 7 mẫu sổ kế toán cụ thể (từ S1-HKD đến S7-HKD). |
|   2 | Tỷ lệ tính thuế trên doanh thu đối với dịch vụ, xây dựng không bao thầu nguyên vật liệu là bao nhiêu? | Config A | 0.80 | 0.80 | 0.70 | 0.70 | retrieval | Dense model nhầm lẫn giữa tỷ lệ của ngành dịch vụ (5% GTGT, 2% TNCN) với ngành phân phối hàng hóa do hai đoạn văn nằm gần nhau trong phụ lục. |
|   3 | Đặt tên cho hộ kinh doanh bị cấm những từ ngữ gì? | Config B | 0.85 | 0.85 | 0.80 | 0.80 | generation | Mô hình trả lời đúng việc cấm từ "công ty", "doanh nghiệp" nhưng quên trích dẫn quy định về việc không được trùng tên trong phạm vi cấp huyện. |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| -------: | ------ | ------------------------------ | --------------- | ------------- |
|        1 | Bổ sung Metadata filter theo số hiệu văn bản (Nghị định / Thông tư) | Case 1 & Case 2 cho thấy câu hỏi luật thường nhắm vào một văn bản cụ thể. | Tăng Context Precision lên > 0.95. | Chạy lại bộ test 15 câu với metadata filtering. |
|        2 | Tinh chỉnh prompt Generation để bắt buộc liệt kê đầy đủ các điều kiện | Case 3 mô hình bỏ sót ý phụ khi trả lời câu hỏi tổng hợp. | Tăng Faithfulness và Answer Relevance lên > 0.96. | Kiểm tra thủ công các câu hỏi dạng điều kiện cấm. |
|        3 | Bổ sung từ điển đồng nghĩa (Synonyms) cho từ khóa thuế và kế toán | Thuế khoán, thuế kê khai, lệ phí môn bài có nhiều thuật ngữ dân gian. | Tăng BM25 recall cho các câu hỏi ngôn ngữ tự nhiên. | Benchmark lại BM25 đơn lẻ trên test set. |

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
| ---------- | -------- | -----------: | -----------------: | ---------- |
| Lost-in-the-middle Document Reordering | Hybrid + RRF không reorder | Faithfulness +0.04 | Latency +10ms, cost không đổi | Đưa tài liệu quan trọng nhất lên đầu và cuối context giúp LLM chú ý tốt hơn, giảm sót thông tin. |
