from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
from agents.slow_mind import SlowMind
from executor.execution_context import ExecutionContext
import re
import logging
import traceback
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
        knowledge_content = await slow_mind.generate_learning_content(topic_info)
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
            parsed_content = clean_and_extract_json(knowledge_content)
        except Exception as e:
            logger.error("生成知识点失败")
            logger.error(traceback.format_exc())  # ✅ 打印完整栈
            raise
        return KnowledgePointGenerateResponse(**parsed_content)
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"知识点生成失败: JSON解析错误 - {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"知识点生成失败: {str(e)}")
def clean_and_extract_json(text: str) -> dict:
    """
    从模型返回的 Markdown 文本中提取 ```json 包裹的 JSON
    保留 JSON 内部所有 Markdown（如 ```html）
    """
    if not text:
        raise ValueError("输入内容为空")

    # ① 优先：```json ... ```
    match = re.search(r"```json\s*(\{[\s\S]*?\})\s*```", text)
    if match:
        json_str = match.group(1)
        return json.loads(json_str)

    # ② 兜底：提取第一个 { ... }
    brace_match = re.search(r"(\{[\s\S]*\})", text)
    if brace_match:
        json_str = brace_match.group(1)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"检测到疑似 JSON，但解析失败: {e}")

    # ③ 最终失败
    raise ValueError("未能从返回内容中提取 JSON")
def extract_json(text: str) -> str:
    """
    从 LLM 返回中安全提取 JSON
    """
    if not text:
        raise ValueError("AI 返回内容为空")

    text = text.strip()

    # 情况1：```json 或 ``` 包裹的内容
    if text.startswith("```"):
        lines = text.splitlines()
        logger.debug("检测到代码块格式，行数: %d", len(lines))

        # 去掉首行 ``` 或 ```json
        if lines[0].startswith("```"):
            lines = lines[1:]

        # 去掉末行 ```
        if lines and lines[-1].strip().endswith("```"):
            lines = lines[:-1]
        elif lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()
        logger.debug("去除代码块后的文本:\n%s", text[:200] + "..." if len(text) > 200 else text)

    # 情况2：查找最外层的 JSON 对象
    # 处理嵌套的情况，找到匹配的 { 和 }
    first = text.find("{")
    if first == -1:
        raise ValueError("未找到 JSON 开始符 '{'")

    brace_count = 0
    last = first
    in_string = False
    escape_next = False

    for i, char in enumerate(text[first:], first):
        if escape_next:
            escape_next = False
            continue

        if char == '\\':
            escape_next = True
            continue

        if char == '"':
            in_string = not in_string
            continue

        if not in_string:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    last = i
                    break

    if brace_count != 0:
        raise ValueError(f"JSON 结构不完整，括号未匹配: {brace_count}")

    result = text[first:last + 1]
    logger.debug("提取的JSON内容长度: %d", len(result))
    logger.debug("提取的JSON内容预览:\n%s", result[:300] + "..." if len(result) > 300 else result)

    return result


def parse_ai_json(raw: str) -> dict:
    """
    安全解析 AI JSON
    """
    try:
        extracted = extract_json(raw)
    except ValueError as e:
        logger.error("JSON提取失败: %s", str(e))
        raise

    # 清理控制字符和其他无效字符
    cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', extracted)

    # 尝试多种修复策略
    json_candidates = [cleaned]

    # 如果清理后的内容有问题，尝试原始提取的内容
    if cleaned != extracted:
        json_candidates.insert(0, extracted)

    # 尝试修复常见的JSON问题
    for candidate in json_candidates[:]:  # 复制列表避免修改时的问题
        # 修复末尾逗号问题
        candidate = re.sub(r',\s*}', '}', candidate)
        candidate = re.sub(r',\s*]', ']', candidate)

        # 修复单引号问题（如果AI使用了单引号）
        # 注意：这个可能会破坏有效的JSON，所以要小心
        if '"' not in candidate and "'" in candidate:
            candidate = candidate.replace("'", '"')

        json_candidates.append(candidate)

    # 尝试解析每个候选
    for i, candidate in enumerate(json_candidates):
        try:
            logger.debug("尝试解析JSON候选 %d", i + 1)
            result = json.loads(candidate)

            # 验证必需字段
            if not isinstance(result, dict):
                continue

            required_fields = ['topic_id', 'title', 'levels']
            missing_fields = [field for field in required_fields if field not in result]
            if missing_fields:
                logger.warning("JSON缺少必需字段: %s", missing_fields)
                continue

            # 验证levels字段
            if not isinstance(result.get('levels'), list):
                logger.warning("levels字段不是数组类型")
                continue

            logger.info("JSON解析成功，使用候选 %d", i + 1)
            return result

        except json.JSONDecodeError as e:
            logger.debug("候选 %d 解析失败: %s", i + 1, str(e))
            continue

    # 所有候选都失败了
    logger.error("所有JSON解析策略都失败")
    logger.error("提取后的JSON内容:\n%s", extracted)
    logger.error("清理后的JSON内容:\n%s", cleaned)

    # 提供更详细的错误信息
    raise ValueError("无法解析AI返回的JSON内容，请检查AI输出格式")