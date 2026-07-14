import json
import os
import sys

from .gemini_config import *
from .prompts import *
from .utils import *


def run_evaluate(
    text_path: str,
    image_path: str,
    output_dir: str,
    limit_samples: int = 1,
    max_retries: int = 3,
):
    """Thực thi pipeline filtering."""
    if limit_samples == 0:
        print("No records to process. Exiting.")
        return

    # ------------------ Read data -----------------------------
    with open(text_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    raw_answers = []
    checkpoint_dir = os.path.join(output_dir, "checkpoints")
    log_file_path = os.path.join(checkpoint_dir, "log.json")
    index_error_path = os.path.join(checkpoint_dir, "index_error.txt")

    os.makedirs(checkpoint_dir, exist_ok=True)

    if not os.path.exists(log_file_path):
        open(log_file_path, "w", encoding="utf-8").close()

    if not os.path.exists(index_error_path):
        open(index_error_path, "w", encoding="utf-8").close()

    all_checkpoints = os.listdir(checkpoint_dir)
    next_checkpoint = len(all_checkpoints) - 1

    if next_checkpoint != 1:
        with open(
            f"{checkpoint_dir}/raw_answers_checkpoint_{next_checkpoint - 1}.json",
            "r",
            encoding="utf-8",
        ) as f:
            raw_answers = json.load(f)
        with open(index_error_path, "r", encoding="utf-8") as file:
            error_index = [int(line.strip()) for line in file]

        open(index_error_path, "w").close()

        previous_index = raw_answers[-1]["index"] if raw_answers else -1
        if limit_samples == -1:
            index = error_index + list(range(previous_index + 1, len(data)))
        else:
            index = error_index + list(
                range(
                    previous_index + 1,
                    min(previous_index + 1 + limit_samples, len(data)),
                )
            )

        print(
            f"Resume from checkpoint_{next_checkpoint - 1} with {len(raw_answers)} entries"
        )
    else:
        raw_answers = []
        index = list(range(len(data)))
        print("No checkpoint found. Start from beginning.")

    save_path = f"{checkpoint_dir}/raw_answers_checkpoint_{next_checkpoint}.json"
    processed_samples = 0
    set_of_error_index = set()

    for i, idx in enumerate(index):
        item = data[idx]
        processed_samples += 1
        if limit_samples != -1 and processed_samples > limit_samples:
            break

        try:
            response = gemini_filtering(image_path, item, idx, log_file_path)
            if response is None:
                trial = 0
                while trial < max_retries:
                    print(f"Retrying item {i} (attempt {trial + 1}/{max_retries})")
                    response = gemini_filtering(image_path, item, idx, log_file_path)
                    if response is not None:
                        break
                    trial += 1
                if trial == max_retries:
                    print(
                        f"Failed to process item {i} after {max_retries} retries. Skipping."
                    )
                    with open(log_file_path, "a", encoding="utf-8") as f:
                        item_link = (
                            item.get("url")
                            or item.get("coco_url")
                            or item.get("image_link")
                            or item.get("link")
                        )
                        error_entry = {
                            "id": idx,
                            "question": item.get("question", ""),
                            "answers": item.get("answers", []),
                            "link": item_link,
                            "error": "Max retries exceeded",
                        }
                        f.write(json.dumps(error_entry, ensure_ascii=False) + "\n")
                        set_of_error_index.add(idx)
                    continue
            if raw_answers:
                if response["index"] > raw_answers[-1]["index"]:
                    raw_answers.append(response)
                else:
                    raw_answers.insert(response["index"], response)
            else:
                raw_answers.append(response)

        except KeyboardInterrupt:
            print("Process interrupted by user. Exiting.")
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(raw_answers, f, ensure_ascii=False, indent=2)
            break

        except Exception as e:
            print(f"Error processing item {idx}: {e}")
            continue

    if raw_answers:
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(raw_answers, f, ensure_ascii=False, indent=2)
        print(f"Results saved to {save_path}")

    if set_of_error_index:
        with open(index_error_path, "w", encoding="utf-8") as f:
            for idx in set_of_error_index:
                f.write(f"{idx}\n")
