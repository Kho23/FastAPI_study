from pydantic import BaseModel, ConfigDict, Field

"""
out 은 응답용, create 는 요청용
(Spring 의 DTO 응답용/요청용 나누는 것과 같은 원리)
"""

class RuleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    keyword: str

class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    rules: list[RuleOut]

class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)

class RuleCreate(BaseModel):
    keyword: str = Field(min_length=1, max_length=50)

class ReclassifyResult(BaseModel):
    updated: int