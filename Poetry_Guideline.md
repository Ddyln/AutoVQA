# Autovqa — Quick Setup (Poetry 2.x + Python 3.10)

## 1. Cài Python 3.10 (nếu chưa có)
a. Cập nhật hệ thống
```bash
sudo apt update && sudo apt upgrade -y
```
b. Cài công cụ thêm PPA
```bash
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
```

c. Cài Python 3.10
```bash
sudo apt install python3.10 python3.10-venv python3.10-dev -y
python3.10 --version
````

---

## 2. Cài Poetry (nếu chưa có)

```bash
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"  # nếu cần
poetry --version
```

---

## 3. Clone dự án

```bash
git clone <URL-repo-cua-ban>
cd autovqa
```

---

## 4. Tạo virtual environment với Python 3.10

```bash
poetry env use python3.10
poetry env list
```

---

## 5. Cài tất cả dependencies (cả dev)

```bash
poetry install --with dev
```

---

## 6. Kích hoạt môi trường

```bash
eval "$(poetry env activate)"
# Prompt sẽ hiển thị tên venv:
# (autovqa-xxxx-py3.10) $
```

---

## 7. Chạy dev tools

```bash
# Kiểm tra Python
python --version

# Format code
black .

# Sắp xếp import
isort .

# Lint code
flake8 .

# Chạy test
pytest
```

> Hoặc thay `black .` bằng `poetry run black .` nếu không muốn activate venv.

---

## 8. Thoát virtual environment

```bash
exit
```

