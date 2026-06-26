from pydantic import BaseModel, field_validator

class IngestRequest(BaseModel):
    file_path: str

    @field_validator("file_path")
    @classmethod
    def file_path_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("file_path cannot be empty")
        return v

class AskRequest(BaseModel):
    question: str
    conversation_id: str = ""

    @field_validator("question")
    @classmethod
    def question_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("question cannot be empty")
        return v
