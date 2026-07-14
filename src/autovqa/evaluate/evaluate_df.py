from autovqa.evaluate.utils import *

# Đường dẫn tuyệt đối tới thư mục
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Tạo thư mục checkpoints tại cùng nơi với file main.py
CHECKPOINT_DIR = os.path.join(CURRENT_DIR, "checkpoints")

LOG_FILE = os.path.join(CHECKPOINT_DIR, "log.json")

INDEX_ERROR = os.path.join(CHECKPOINT_DIR, "index_error.txt")


all_checkpoints = os.listdir(CHECKPOINT_DIR)
current_checkpoint = len(all_checkpoints) - 1
# current_checkpoint = 1
print(f"Current checkpoint: {current_checkpoint}")

with open(
    f"{CHECKPOINT_DIR}/raw_answers_checkpoint_{current_checkpoint}.json",
    "r",
    encoding="utf-8",
) as f:
    raw_answers = json.load(f)

print(f"Number of records: {len(raw_answers)}")

df, removed_cols = json_list_to_dataframe(raw_answers, is_remove_empty_cols=True)
print(f"Number of rows in DataFrame: {len(df)}")
print(f"Removed columns: {removed_cols}")
print(f"Number of columns in DataFrame after removal: {len(df.columns)}")

status, invalid_rows = is_invalid_row(df)
if status:
    print("DataFrame contains invalid rows. Saving invalid rows to log file.")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        json.dump({"invalid_rows": invalid_rows}, f, ensure_ascii=False, indent=2)
else:
    print("DataFrame is valid.")
