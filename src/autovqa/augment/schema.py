from typing import List, Literal

from pydantic import BaseModel, Field

AllowedCategories = Literal[
    "Xác định đối tượng/ thuộc tính",
    "Mô tả vị trí/ không gian",
    "Mô tả hành động",
    "Xác định số lượng",
    "Câu hỏi có/không",
    "Câu hỏi so sánh",
    "Mối quan hệ",
    "Lý do/ Nhân quả",
    "Suy luận ngữ cảnh",
]


class VQA(BaseModel):
    question: str = Field(..., description="The question in natural Vietnamese.")
    answer: List[str] = Field(
        ..., min_length=5, max_length=5, description="Exactly 5 short answers"
    )
    category: AllowedCategories = Field(
        ..., description="The category of the question."
    )
    reason_depth: int = Field(..., ge=1, le=5, description="The reasoning level (1-5).")
