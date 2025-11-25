## Image Preprocessing Pipeline

### 1. Giới thiệu

Pipeline xử lý ảnh: resize, pad, denoise, color correction, sharpening, normalize.
Có thể gọi bằng Python hoặc chạy trực tiếp bằng CLI.

---

### 2. Cài đặt môi trường

```bash
pip install -r requirements.txt
```

Yêu cầu tối thiểu:

```txt
opencv-python
numpy
```

---

### 3. Import trong Python

```python
from src.preprocessing.image.main import preprocess_image, run_pipeline

# Xử lý 1 ảnh đơn lẻ
img = preprocess_image("sample.jpg", target_size=(480, 640), do_normalize=True)

# Chạy pipeline trên toàn bộ thư mục ảnh
run_pipeline(do_normalize=False)
```

---

### 4. Chạy bằng CLI

```bash
python -m autovqa.preprocessing.image.main
```

---

### 5. Ghi chú

* Input/output folder được định nghĩa trong `/AutoVQA/src/autovqa/config/config.py`.
* `target_size` mặc định sẽ tìm kích thước phổ biến nhất trong folder, nếu không có thì dùng `(480, 640)`.
* Nếu `do_normalize=True`, ảnh sẽ được chuẩn hóa về `[0, 1]` trước khi lưu lại.

**How to activate env by poetry**
```bash
eval "$(poetry env activate)"
```