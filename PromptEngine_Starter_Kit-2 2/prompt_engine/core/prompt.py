from pydantic import BaseModel
from typing import Dict, Any, List

class PromptObject(BaseModel):
    id: str
    template: str
    params: Dict[str, Any]
    version: str
    reasoning: str
    result: str
    qa_passed: bool
    brand_tag: str
    memory_context: Dict[str, Any]
    feedback: List[str]
    timestamp: str
