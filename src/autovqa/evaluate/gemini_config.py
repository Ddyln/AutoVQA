import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from autovqa.evaluate.config import *
from autovqa.evaluate.prompts import *
from autovqa.evaluate.utils import *

# Load environment variables from .env file
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash")
THINKING_BUDGET = int(os.getenv("THINKING_BUDGET", "0"))

if GOOGLE_API_KEY:
    client = genai.Client(api_key=GOOGLE_API_KEY)
else:
    client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION,
    )


def gemini_filtering(image_path, entry, idx, log_file_path):
    question = entry.get("question", "")
    answers = entry.get("answers", [])
    link = (
        entry.get("url")
        or entry.get("coco_url")
        or entry.get("image_link")
        or entry.get("link")
    )

    if not link:
        print(
            f"Error: Missing image link key for item {idx}. Expected one of: url, coco_url, image_link, link"
        )
        error_entry = {
            "id": idx,
            "question": question,
            "answers": answers,
            "link": None,
            "error": "Missing image link key (url/coco_url/image_link/link)",
        }
        with open(log_file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(error_entry, ensure_ascii=False) + "\n")
        return None

    image_name = entry.get("image_name") or os.path.basename(link)
    image_full_path = os.path.join(image_path, image_name)

    print(f"Processing image {idx}: {link}")

    try:
        with open(image_full_path, "rb") as f:
            image_bytes = f.read()
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_full_path}. Skipping.")
        # Lưu entry lỗi
        error_entry = {
            "id": idx,
            "question": question,
            "answers": answers,
            "link": link,
            "error": "Image file not found",
        }
        with open(log_file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(error_entry, ensure_ascii=False) + "\n")

        return None

    image = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")

    combined_prompt_string = COMBINED_EVALUATION_TEMPLATE.substitute(
        EVALUATE_IMAGE_PROMPT_CONTENT=EVALUATE_IMAGE_PROMPT,
        IMAGE_DIVERSITY_PROMPT_CONTENT=IMAGE_DIVERSITY_PROMPT,
        EVALUATE_TEXT_PROMPT_CONTENT=EVALUATE_TEXT_PROMPT,
        VISUAL_QUESTION_ANSWER_CORRELATION_CONTENT=VISUAL_QUESTION_ANSWER_CORRELATION,
        question=question,
        answers=json.dumps(answers, ensure_ascii=False),
    )

    try:
        response_combined = client.models.generate_content(
            # model="gemini-2.5-flash-lite-preview-06-17",
            model="gemini-2.5-flash",
            contents=[combined_prompt_string, image],
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            ),
        )

        combined_result = parse_json(response_combined)

        combined_result["image_link"] = link  # Thêm link ảnh vào kết quả
        combined_result["image_name"] = image_name  # Thêm tên ảnh vào kết quả
        combined_result["question"] = question  # Thêm câu hỏi vào kết quả
        combined_result["answers"] = answers  # Thêm câu trả lời vào kết quả
        combined_result["index"] = idx

        # Trích xuất các khóa cần thiết từ kết quả (thật ra combined_result đã đúng nhưng thêm bước này để chắc chắn hơn về định dạng)
        final_result = extract_keys(combined_result)
        return final_result

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response for {image_name}: {e}")
        if response_combined and hasattr(response_combined, "text"):
            print(f"Raw response text: {response_combined.text}")
        else:
            print("No raw response text available.")

        # Lưu entry lỗi
        error_entry = {
            "id": idx,
            "question": question,
            "answers": answers,
            "link": link,
            "error": str(e),
        }
        with open(log_file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(error_entry, ensure_ascii=False) + "\n")

        return None

    except Exception as e:
        print(f"An unexpected error occurred for {image_name}: {e}")
        if response_combined and hasattr(response_combined, "text"):
            print(f"Raw response text: {response_combined.text}")
        else:
            print("No raw response text available.")

        # Lưu entry lỗi
        error_entry = {
            "id": idx,
            "question": question,
            "answers": answers,
            "link": link,
            "error": str(e),
        }
        with open(log_file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(error_entry, ensure_ascii=False) + "\n")

        return None
