from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
from agents.slow_mind import SlowMind
from executor.execution_context import ExecutionContext
import re
import logging

logger = logging.getLogger(__name__)

learning_router = APIRouter()

class KnowledgePointGenerateRequest(BaseModel):
    id: str
    label: str
    type: str
    select_element: List[str]

class KnowledgePointGenerateResponse(BaseModel):
    topic_id: str
    title: str
    levels: List[Dict[str, Any]]

@learning_router.post("/generate-knowledge-point", response_model=KnowledgePointGenerateResponse)
async def generate_knowledge_point(request: KnowledgePointGenerateRequest):
    """
    根据知识点ID和选择的元素生成学习内容
    
    参数：
    - id: 知识点ID
    - label: 知识点标签
    - type: 知识点类型
    - select_element: 选择的元素列表
    """
    try:
        # 初始化AI执行上下文
        context = ExecutionContext()
        slow_mind = SlowMind(context)
        
        # 构造知识点信息
        topic_info = {
            "id": request.id,
            "label": request.label,
            "type": request.type,
            "select_element": request.select_element
        }
            
        # 生成知识点内容
        knowledge_content = slow_mind.generate_learning_content(topic_info)
        print("Generated Knowledge Content:", knowledge_content)
        # # 解析AI返回的JSON字符串
        # import re
        # # 尝试提取可能包含在markdown代码块中的JSON
        # json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', knowledge_content, re.DOTALL)
        # if json_match:
        #     knowledge_json_str = json_match.group(1)
        # else:
        #     # 如果没有找到markdown代码块，尝试直接解析整个字符串
        #     knowledge_json_str = knowledge_content.strip()
            
        # # 解析JSON字符串为Python对象
        # parsed_content = json.loads(knowledge_json_str)
        try:
            parsed_content = parse_ai_json(knowledge_content)
        except Exception as e:
            logger.error("AI知识点生成失败", exc_info=True)
            raise RuntimeError("AI返回的知识点JSON不合法") from e
        return KnowledgePointGenerateResponse(**parsed_content)
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"知识点生成失败: JSON解析错误 - {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"知识点生成失败: {str(e)}")
def extract_json(text: str) -> str:
    """
    从 LLM 返回中安全提取 JSON
    """
    if not text:
        raise ValueError("AI 返回内容为空")

    text = text.strip()

    # 情况1：```json 包裹
    if text.startswith("```"):
        lines = text.splitlines()
        # 去掉首行 ``` 或 ```json
        if lines[0].startswith("```"):
            lines = lines[1:]
        # 去掉末行 ```
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    # 情况2：尝试从第一个 { 到最后一个 }
    first = text.find("{")
    last = text.rfind("}")
    if first == -1 or last == -1 or last <= first:
        raise ValueError("未找到完整 JSON 结构")

    return text[first:last + 1]


def parse_ai_json(raw: str) -> dict:
    """
    安全解析 AI JSON
    """
    extracted = extract_json(raw)
    try:
        return json.loads(extracted)
    except json.JSONDecodeError as e:
        logger.error("JSON解析失败")
        logger.error("提取后的JSON内容:\n%s", extracted)
        raise