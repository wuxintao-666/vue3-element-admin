from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from db.database import get_db, SessionLocal
from db.models import ProgrammingExercise as TestQuestionModel, Course as CourseModel, KGNode
from schemas.programming_exercise_schema import (
    ProgrammingExerciseCreate, ProgrammingExerciseUpdate, ProgrammingExerciseResponse,
    ProgrammingExercisePageQuery, ProgrammingExercisePageResponse, ApiResponse,
    ProgrammingExerciseBatchSave
)
from utils.config_loader import load_config
from agents.slow_mind import SlowMind
from executor.execution_context import ExecutionContext

test_question_router = APIRouter(prefix="/api/v1/test-questions", tags=["Test Questions"])

# logger
logger = logging.getLogger(__name__)


@test_question_router.get("/", response_model=ApiResponse)
async def get_test_questions(
    course_id: Optional[str] = None,
    node_id: Optional[str] = None,
    pageNum: int = 1,
    pageSize: int = 10,
    db: Session = Depends(get_db)
):
    """
    获取测试题分页列表
    """
    try:
        config = load_config()
        test_course_id = config.get("TEST_COURSE_ID", "TEST001")

        query = db.query(TestQuestionModel)

        # 如果没有指定course_id，使用TEST_COURSE_ID
        if not course_id:
            course_id = test_course_id

        # 根据course_code查找course_id
        course = db.query(CourseModel).filter(CourseModel.course_code == course_id).first()
        if course:
            query = query.filter(TestQuestionModel.course_id == course.id)

        if node_id:
            query = query.filter(TestQuestionModel.node_id == node_id)

        total = query.count()
        offset = (pageNum - 1) * pageSize
        questions = query.order_by(TestQuestionModel.created_at.desc()).offset(offset).limit(pageSize).all()

        question_list = []
        for question in questions:
            question_dict = ProgrammingExerciseResponse.from_orm(question).dict(by_alias=True)
            # 添加course_code
            if course:
                question_dict['course_code'] = course.course_code
            question_list.append(question_dict)

        return ApiResponse(
            code="00000",
            data={
                "list": question_list,
                "total": total
            },
            message="获取成功"
        )
    except Exception as e:
        logger.error(f"获取测试题列表失败: {str(e)}")
        return ApiResponse(
            code="A0001",
            message=f"获取测试题列表失败: {str(e)}"
        )


@test_question_router.get("/{question_id}", response_model=ApiResponse)
async def get_test_question(question_id: int, db: Session = Depends(get_db)):
    """
    获取测试题详情
    """
    try:
        question = db.query(TestQuestionModel).filter(TestQuestionModel.id == question_id).first()

        if not question:
            return ApiResponse(
                code="A0001",
                message="测试题不存在"
            )

        question_data = ProgrammingExerciseResponse.from_orm(question)
        return ApiResponse(
            code="00000",
            data=question_data.dict(by_alias=True),
            message="获取成功"
        )
    except Exception as e:
        logger.error(f"获取测试题详情失败: {str(e)}")
        return ApiResponse(
            code="A0001",
            message=f"获取测试题详情失败: {str(e)}"
        )


@test_question_router.post("/", response_model=ApiResponse)
async def create_test_question(question_data: ProgrammingExerciseCreate, db: Session = Depends(get_db)):
    """
    创建测试题
    """
    try:
        config = load_config()
        test_course_id = config.get("TEST_COURSE_ID", "TEST001")

        # 如果没有指定course_id，使用TEST_COURSE_ID
        if not question_data.course_id:
            question_data.course_id = test_course_id

        # 根据course_code查找课程
        course = db.query(CourseModel).filter(CourseModel.course_code == question_data.course_id).first()
        if not course:
            return ApiResponse(
                code="A0001",
                message=f"课程代码 {question_data.course_id} 不存在"
            )

        # 检查节点是否存在于知识图谱中
        node = db.query(KGNode).filter(
            KGNode.course_id == course.id,
            KGNode.id == question_data.node_id
        ).first()

        if not node:
            return ApiResponse(
                code="A0001",
                message=f"节点 '{question_data.node_id}' 在课程 '{question_data.course_id}' 的知识图谱中不存在"
            )

        # 检查是否已存在相同course_id和node_id的记录（一个节点只能有一道测试题）
        existing_question = db.query(TestQuestionModel).filter(
            TestQuestionModel.course_id == course.id,
            TestQuestionModel.node_id == question_data.node_id
        ).first()

        if existing_question:
            return ApiResponse(
                code="A0001",
                message=f"该课程的节点 '{question_data.node_id}' 已存在测试题，不能重复创建"
            )

        new_question = TestQuestionModel(
            course_id=course.id,
            node_id=question_data.node_id,
            title=question_data.title,
            description_md=question_data.description_md,
            start_code_html=question_data.start_code_html,
            start_code_css=question_data.start_code_css,
            start_code_js=question_data.start_code_js,
            checkpoints=question_data.checkpoints,
            answer_html=question_data.answer_html,
            answer_css=question_data.answer_css,
            answer_js=question_data.answer_js
        )

        db.add(new_question)
        db.commit()
        db.refresh(new_question)

        return ApiResponse(
            code="00000",
            data={"id": new_question.id},
            message="创建成功"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"创建测试题失败: {str(e)}")
        return ApiResponse(
            code="A0001",
            message=f"创建测试题失败: {str(e)}"
        )


@test_question_router.put("/{question_id}", response_model=ApiResponse)
async def update_test_question(question_id: int, question_data: ProgrammingExerciseUpdate, db: Session = Depends(get_db)):
    """
    更新测试题
    """
    try:
        question = db.query(TestQuestionModel).filter(TestQuestionModel.id == question_id).first()

        if not question:
            return ApiResponse(
                code="A0001",
                message="测试题不存在"
            )

        update_fields = question_data.dict(exclude_unset=True)

        # 准备新的course_id和node_id用于验证
        new_course_id = question.course_id
        new_node_id = question.node_id

        for key, value in update_fields.items():
            if key == "course_id":
                # 根据course_code查找course_id
                course = db.query(CourseModel).filter(CourseModel.course_code == value).first()
                if course:
                    new_course_id = course.id
                    setattr(question, "course_id", course.id)
                else:
                    return ApiResponse(
                        code="A0001",
                        message=f"课程代码 {value} 不存在"
                    )
            elif key == "node_id":
                new_node_id = value
                setattr(question, key, value)
            else:
                setattr(question, key, value)

        # 检查更新后的节点是否存在于知识图谱中
        node = db.query(KGNode).filter(
            KGNode.course_id == new_course_id,
            KGNode.id == new_node_id
        ).first()

        if not node:
            return ApiResponse(
                code="A0001",
                message=f"节点 '{new_node_id}' 在知识图谱中不存在，无法更新"
            )

        # 检查更新后的course_id和node_id组合是否与其他记录冲突（排除当前记录）
        if (new_course_id != question.course_id or new_node_id != question.node_id):
            existing = db.query(TestQuestionModel).filter(
                TestQuestionModel.course_id == new_course_id,
                TestQuestionModel.node_id == new_node_id,
                TestQuestionModel.id != question_id
            ).first()

            if existing:
                return ApiResponse(
                    code="A0001",
                    message=f"该课程的节点 '{new_node_id}' 已存在其他测试题，无法更新"
                )

        question.updated_at = datetime.now()
        db.commit()

        return ApiResponse(
            code="00000",
            message="更新成功"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"更新测试题失败: {str(e)}")
        return ApiResponse(
            code="A0001",
            message=f"更新测试题失败: {str(e)}"
        )


@test_question_router.delete("/{question_ids}", response_model=ApiResponse)
async def delete_test_questions(question_ids: str, db: Session = Depends(get_db)):
    """
    删除测试题（支持批量删除，用逗号分隔）
    """
    try:
        ids = [int(id.strip()) for id in question_ids.split(",")]
        deleted_count = db.query(TestQuestionModel).filter(TestQuestionModel.id.in_(ids)).delete(synchronize_session=False)
        db.commit()

        if deleted_count == 0:
            return ApiResponse(
                code="A0001",
                message="未找到要删除的测试题"
            )

        return ApiResponse(
            code="00000",
            message="删除成功"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"删除测试题失败: {str(e)}")
        return ApiResponse(
            code="A0001",
            message=f"删除测试题失败: {str(e)}"
        )


@test_question_router.post("/batch-generate", response_model=ApiResponse)
async def batch_generate_test_questions(
    node_ids: List[str],
    course_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    批量并发生成测试题
    """
    try:
        config = load_config()
        test_course_id = config.get("TEST_COURSE_ID", "TEST001")

        # 如果没有指定course_id，使用TEST_COURSE_ID
        if not course_id:
            course_id = test_course_id

        # 根据course_code查找课程
        course = db.query(CourseModel).filter(CourseModel.course_code == course_id).first()
        if not course:
            return ApiResponse(
                code="A0001",
                message=f"课程代码 {course_id} 不存在"
            )

        # 获取所有有效的节点信息
        valid_nodes = []
        for node_id in node_ids:
            node = db.query(KGNode).filter(
                KGNode.course_id == course.id,
                KGNode.id == node_id
            ).first()

            if node:
                # 检查是否已存在测试题
                existing = db.query(TestQuestionModel).filter(
                    TestQuestionModel.course_id == course.id,
                    TestQuestionModel.node_id == node_id
                ).first()

                if not existing:
                    valid_nodes.append({
                        "id": node.id,
                        "label": node.label,
                        "type": node.type.value if hasattr(node.type, 'value') else str(node.type)
                    })

        if not valid_nodes:
            return ApiResponse(
                code="A0001",
                message="没有有效的节点可以生成测试题"
            )

        # 初始化SlowMind
        context = ExecutionContext()
        slow_mind = SlowMind(context)

        # 并发生成测试题
        async def generate_single_test_question(node_info):
            """为单个节点生成测试题"""
            try:
                # 生成测试任务
                test_task_data = await slow_mind.generate_test_tasks(node_info)

                if test_task_data and "tasks" in test_task_data and test_task_data["tasks"]:
                    # 取第一个任务作为测试题
                    first_task = test_task_data["tasks"][0] if test_task_data["tasks"] else None

                    if first_task:
                        # 创建测试题记录
                        question_data = {
                            "course_id": course.id,
                            "node_id": node_info["id"],
                            "title": first_task.get("title", f"{node_info['label']}测试题"),
                            "description_md": first_task.get("description", ""),
                            "start_code_html": first_task.get("start_code", {}).get("html", ""),
                            "start_code_css": first_task.get("start_code", {}).get("css", ""),
                            "start_code_js": first_task.get("start_code", {}).get("js", ""),
                            "checkpoints": first_task.get("checkpoints", []),
                            "answer_html": first_task.get("answer", {}).get("html", ""),
                            "answer_css": first_task.get("answer", {}).get("css", ""),
                            "answer_js": first_task.get("answer", {}).get("js", "")
                        }

                        # 在独立的数据库会话中保存
                        db_session = SessionLocal()
                        try:
                            new_question = TestQuestionModel(**question_data)
                            db_session.add(new_question)
                            db_session.commit()
                            db_session.refresh(new_question)
                            logger.info(f"成功生成测试题: {node_info['id']}")
                            return {"success": True, "node_id": node_info["id"], "question_id": new_question.id}
                        except Exception as e:
                            db_session.rollback()
                            logger.error(f"保存测试题失败 {node_info['id']}: {str(e)}")
                            return {"success": False, "node_id": node_info["id"], "error": str(e)}
                        finally:
                            db_session.close()
                    else:
                        return {"success": False, "node_id": node_info["id"], "error": "生成的测试题为空"}
                else:
                    return {"success": False, "node_id": node_info["id"], "error": "AI生成失败"}
            except Exception as e:
                logger.error(f"生成测试题异常 {node_info['id']}: {str(e)}")
                return {"success": False, "node_id": node_info["id"], "error": str(e)}

        # 并发执行所有生成任务
        tasks = [generate_single_test_question(node_info) for node_info in valid_nodes]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 统计结果
        success_count = 0
        failed_results = []

        for result in results:
            if isinstance(result, Exception):
                logger.error(f"任务执行异常: {str(result)}")
                failed_results.append({"error": str(result)})
            elif result["success"]:
                success_count += 1
            else:
                failed_results.append(result)

        return ApiResponse(
            code="00000",
            message=f"批量生成完成，成功生成 {success_count} 道测试题",
            data={
                "success_count": success_count,
                "total_requested": len(node_ids),
                "valid_nodes": len(valid_nodes),
                "failed": failed_results
            }
        )

    except Exception as e:
        logger.error(f"批量生成测试题失败: {str(e)}")
        return ApiResponse(
            code="A0001",
            message=f"批量生成测试题失败: {str(e)}"
        )