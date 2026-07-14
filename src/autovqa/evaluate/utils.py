import json
import re

import pandas as pd

from .config import *


def parse_json(response):
    try:
        answer = response.text
        answer = answer.replace("“", '"').replace("”", '"')  # Replace fancy quotes

        # Trích phần JSON đầu tiên giữa ```json ... ```
        match = re.search(r"\{.*\}", answer, re.DOTALL)
        if not match:
            raise ValueError("No JSON object found in the response text.")

        json_str = match.group(0)
        result = json.loads(json_str)
        return result
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        return None
    except Exception as e:
        print(f"Other error in parse_json: {e}")
        return None


def json_list_to_dataframe(json_list, is_remove_empty_cols=False):
    """
    Chuyển danh sách JSON lồng nhau thành DataFrame phẳng.
    Mỗi cấp key được nối bằng dấu gạch dưới (_).
    Đảm bảo không tách chuỗi theo định dạng "Key: Value; Key: Value".
    """

    def flatten_dict(d, parent_key="", sep="_"):
        items = {}
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.update(flatten_dict(v, new_key, sep=sep))
            else:
                # Nếu là chuỗi dạng mô tả, không cố gắng xử lý thêm
                items[new_key] = v
        return items

    flattened = [flatten_dict(entry) for entry in json_list]
    df = pd.DataFrame(flattened)

    if not is_remove_empty_cols:
        return df

    # Vì trong quá trình prompt có thể có các cột không nhất quán, nên ta sẽ loại bỏ các cột không có dữ liệu. Hoặc trong quá trình flatten có thể tạo ra các cột không có dữ liệu.
    # Xóa các cột có tỷ lệ NaN > 90%
    df = df.loc[:, df.isnull().mean() <= 0.9]

    removed_cols = df.columns[df.isnull().mean() > 0.9].tolist()

    return df, removed_cols


def extract_keys(data):
    keys_to_extract = {
        "image_quality_evaluation": {
            "img_clarity": ["Score", "Reason"],
            "img_occlusion": ["Score", "Reason"],
            "img_diff_ability": ["Score", "Reason"],
            "img_object_density": ["Score"],
            "img_interaction_level": ["Score", "Reason"],
            "img_scene_clutter": ["Score"],
        },
        "image_diversity_evaluation": [
            "Img_scene_type",
            "Img_main_object",
            "Image_mainobj_descrip",
            "Cultural_context",
            "Demographic_signals",
            "Scene_typicality_score",
        ],
        "text_quality_evaluation": {
            "txt_grammar": [
                "Score_for_question",
                "Reason_for_question",
                "Score_for_answers",
                "Reason_for_answers",
            ],
            "txt_unambiguity": [
                "Score_for_question",
                "Reason_for_question",
                "Score_for_answers",
                "Reason_for_answers",
            ],
            "txt_qa_structure": [
                "Score_for_question",
                "Reason_for_question",
                "Score_for_answers",
                "Reason_for_answers",
            ],
            "syntactic_complexity": [
                "Score_for_question",
                "Reason_for_question",
                "Score_for_answers",
                "Reason_for_answers",
            ],
            "language_naturalness": [
                "Score_for_question",
                "Reason_for_question",
                "Score_for_answers",
                "Reason_for_answers",
            ],
        },
        "correlation_evaluation": {
            "question_to_image": ["response", "reason"],
            "answer_to_image": ["response", "overall_response", "reason"],
            "question_to_answer": ["response", "overall_response", "reason"],
            "guess_the_answer": ["response", "reason"],
            "reason_depth": ["response", "reason"],
        },
        "image_link": True,
        "image_name": True,
        "question": True,
        "answers": True,
        "index": True,
    }

    def pick(d, spec):
        if isinstance(spec, list):
            return {k: d.get(k) for k in spec if k in d}
        elif isinstance(spec, dict):
            return {k: pick(d.get(k, {}), sub_spec) for k, sub_spec in spec.items()}
        elif spec is True:
            return d
        return None

    return pick(data, keys_to_extract)


# Tập hợp các cột chỉ chứa giá trị số (gồm giá trị đánh giá cho image + text quality và reason depth)
number_columns = [
    "image_quality_evaluation_img_clarity_Score",
    "image_quality_evaluation_img_occlusion_Score",
    "image_quality_evaluation_img_diff_ability_Score",
    "image_quality_evaluation_img_object_density_Score",
    "image_quality_evaluation_img_interaction_level_Score",
    "image_quality_evaluation_img_scene_clutter_Score",
    "image_diversity_evaluation_Scene_typicality_score",
    "text_quality_evaluation_txt_grammar_Score_for_question",
    "text_quality_evaluation_txt_unambiguity_Score_for_question",
    "text_quality_evaluation_txt_qa_structure_Score_for_question",
    "text_quality_evaluation_syntactic_complexity_Score_for_question",
    "text_quality_evaluation_language_naturalness_Score_for_question",
    "correlation_evaluation_reason_depth_response",
]

# Tập hợp các cột chứa list số (là các cột chứa điểm đánh giá cho answers)
list_number_columns = [
    "text_quality_evaluation_txt_grammar_Score_for_answers",
    "text_quality_evaluation_txt_unambiguity_Score_for_answers",
    "text_quality_evaluation_txt_qa_structure_Score_for_answers",
    "text_quality_evaluation_syntactic_complexity_Score_for_answers",
    "text_quality_evaluation_language_naturalness_Score_for_answers",
]

# Tập hợp chỉ chứa các cột chỉ chứa các giá trị yes/no
yes_no_columns = [
    "correlation_evaluation_question_to_image_response",
    "correlation_evaluation_answer_to_image_overall_response",
    "correlation_evaluation_question_to_answer_overall_response",
    "correlation_evaluation_guess_the_answer_response",
]


def is_invalid_row(df):
    def check_row(row):
        try:
            row_lists = row.tolist()

            # Nếu bất kỳ phần tử nào không phải list, thì dòng đó không hợp lệ
            if not all(isinstance(x, list) for x in row_lists):
                return True

            # Nếu bất kỳ list nào rỗng, thì dòng đó không hợp lệ
            if any(len(x) == 0 for x in row_lists):
                return True

            # Kiểm tra độ dài các list
            lengths = [len(x) for x in row_lists]
            return len(set(lengths)) != 1  # True nếu độ dài không đều

        except Exception:
            return True  # Nếu có lỗi thì cũng coi như không hợp lệ

    # Áp dụng hàm kiểm tra
    mask_invalid = df[list_number_columns].apply(check_row, axis=1)

    # Lấy ra các dòng có vấn đề
    df_invalid_rows = df[mask_invalid]
    if df_invalid_rows["index"].tolist():
        # print(f"Rows that are invalid: {df_invalid_rows['index'].tolist()}")
        return True, df_invalid_rows["index"].tolist()
    else:
        # print("No invalid rows found.")
        return False, []
