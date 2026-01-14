import base64
import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from loguru import logger
from openai import OpenAI, RateLimitError

from autovqa.augment.config import (
    get_openai_api_key,
    get_openai_generation_settings,
    get_qa_settings,
)
from autovqa.augment.schema import VQA


class AugmentClient:
    def __init__(self, service_name: str = "gemini"):
        self.service_name = service_name
        self.api_key = get_openai_api_key(service_name)
        self.generation_settings = get_openai_generation_settings(service_name)
        self.qa_settings = get_qa_settings()
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )

        self.total_remains_samples = self.qa_settings.get(
            "total_samples", [2, 2, 2, 2, 2]
        )
        self.probabilities = self.qa_settings.get(
            "probabilities", [0.2, 0.2, 0.2, 0.2, 0.2]
        )
        self.entry_idx = 0

    @staticmethod
    def encode_image(image_path: Path) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def get_target_levels(self) -> Optional[int]:
        available_samples = sum(self.total_remains_samples)
        if available_samples == 0:
            logger.info("No remaining samples to generate.")
            return None

        avaliable_levels = [
            i + 1 for i, count in enumerate(self.total_remains_samples) if count > 0
        ]
        if avaliable_levels == []:
            logger.info("No remaining samples to generate.")
            return None

        target_level = random.choices(
            population=avaliable_levels,
            weights=[self.probabilities[i - 1] for i in avaliable_levels],
            k=1,
        )

        for level in target_level:
            self.total_remains_samples[level - 1] -= 1

        return target_level[0]

    def generate_response(self, image_path: Union[str, Path]):
        if isinstance(image_path, str):
            image_path = Path(image_path)

        if not image_path.exists() or not image_path.is_file():
            logger.error(f"Invalid image path: {image_path}")
            return None

        target_level = self.get_target_levels()
        if target_level is None:
            return None

        user_prompt = str(self.qa_settings.get("user_prompt")).format(
            target_level=target_level
        )

        system_prompt = str(self.qa_settings.get("system_prompt"))
        base64_image = self.encode_image(image_path)

        try:
            completion = self.client.beta.chat.completions.parse(
                model=self.generation_settings.get(
                    "model_name", "models/gemini-3-flash-preview"
                ),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                        ],
                    },
                ],
                response_format=VQA,
            )

            logger.debug("Response generated.")
            logger.debug(f"Remained samples per level: {self.total_remains_samples}")

            return completion

        except RateLimitError as e:
            logger.error(f"Rate is limited: {e.body}")
            return None
        except Exception as e:
            logger.error(f"Error during generation: {e}")
            return None

    def format_response(
        self, json_response: Dict[str, Any], image_path: str
    ) -> List[Dict[str, Any]]:
        try:
            content_str = json_response["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            print(f"Error: Invalid API response structure. Details: {e}")
            return []

        try:
            parsed_content: Union[Dict[str, Any], List[Dict[str, Any]]] = json.loads(
                content_str
            )
        except json.JSONDecodeError as e:
            print(f"Error: Content string is not valid JSON. Details: {e}")
            return []

        if isinstance(parsed_content, dict):
            qa_items = [parsed_content]
        else:
            qa_items = parsed_content

        results: List[Dict[str, Any]] = []

        for item in qa_items:
            formatted_entry: Dict[str, Any] = {
                "question": item.get("question"),
                "answers": item.get("answer", []),
                "category": item.get("category"),
                "coco_url": image_path,
                "index": self.entry_idx,
            }

            results.append(formatted_entry)
            self.entry_idx += 1

        return results

    def run_pipeline(
        self, image_folder_dir: Union[str, Path], output_json_path: Union[str, Path]
    ) -> List[Dict[str, Any]]:
        if isinstance(image_folder_dir, str):
            image_folder_dir = Path(image_folder_dir)

        if not image_folder_dir.exists() or not image_folder_dir.is_dir():
            logger.error(f"Invalid image folder dir: {image_folder_dir}")
            return []

        if isinstance(output_json_path, str):
            output_json_path = Path(output_json_path)

        if not output_json_path.parent.exists():
            output_json_path.parent.mkdir(parents=True, exist_ok=True)

        results: list[dict[Any, Any]] = []

        for image_dir in image_folder_dir.iterdir():
            logger.info(f"Processing image: {image_dir}")

            if sum(self.total_remains_samples) == 0:
                logger.info("All target samples have been generated.")
                break

            response = self.generate_response(image_dir)

            if response is not None:
                results.extend(
                    self.format_response(
                        json_response=response.model_dump(), image_path=str(image_dir)
                    )
                )

        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

        return results


if __name__ == "__main__":
    client = AugmentClient("gemini")
    results = client.run_pipeline(
        "/home/nqthinh/Projects/AutoVQA/sample_images",
        "/home/nqthinh/Projects/AutoVQA/output/augmented_vqa.json",
    )
