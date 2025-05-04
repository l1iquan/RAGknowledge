from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from src.retriever.vector_search import VectorRetriever
from src.utils.helpers import format_retrieval_results
from src.rag.pipeline import RAGPipeline
from src.llm.openai import OpenAILLM
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="法律文档检索系统",
    description="基于向量检索的法律文档检索系统API",
    version="1.0.0"
)

# 添加 CORS 支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境中应该限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化检索器和RAG系统
retriever = None
rag_pipeline = None
llm = None

class SearchQuery(BaseModel):
    """搜索查询模型"""
    query: str
    top_k: Optional[int] = None
    min_score: Optional[float] = None
    include_metadata: Optional[bool] = False

class BatchSearchQuery(BaseModel):
    """批量搜索查询模型"""
    queries: List[str]
    top_k: Optional[int] = None
    min_score: Optional[float] = None
    include_metadata: Optional[bool] = False

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化检索器和RAG系统"""
    global retriever, rag_pipeline, llm
    try:
        retriever = VectorRetriever()
        logger.info("检索器初始化成功")

        rag_pipeline = RAGPipeline()
        logger.info("RAG系统初始化成功")

        llm = OpenAILLM()
        logger.info("LLM初始化成功")
    except Exception as e:
        logger.error(f"初始化失败: {str(e)}")
        raise

@app.get("/api")
async def api_root():
    """API根路径"""
    return {"message": "欢迎使用法律文档检索系统API"}

@app.post("/search")
async def search(query: SearchQuery):
    """单条查询接口

    Args:
        query: 搜索查询参数

    Returns:
        检索结果列表
    """
    if not retriever:
        raise HTTPException(status_code=500, detail="检索器未初始化")

    try:
        results = retriever.retrieve(
            query=query.query,
            top_k=query.top_k,
            min_score=query.min_score
        )
        formatted_results = format_retrieval_results(
            results=results,
            include_metadata=query.include_metadata
        )
        return {"results": formatted_results}
    except Exception as e:
        logger.error(f"搜索失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch-search")
async def batch_search(query: BatchSearchQuery):
    """批量查询接口

    Args:
        query: 批量搜索查询参数

    Returns:
        每个查询的检索结果列表
    """
    if not retriever:
        raise HTTPException(status_code=500, detail="检索器未初始化")

    try:
        all_results = retriever.batch_retrieve(
            queries=query.queries,
            top_k=query.top_k,
            min_score=query.min_score
        )
        formatted_results = [
            format_retrieval_results(results, query.include_metadata)
            for results in all_results
        ]
        return {"results": formatted_results}
    except Exception as e:
        logger.error(f"批量搜索失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

class AskQuery(BaseModel):
    """问答查询模型"""
    query: str
    compare: bool = True

@app.post("/api/ask")
async def ask(query: AskQuery):
    """问答接口，支持RAG和直接LLM对比

    Args:
        query: 问答查询参数

    Returns:
        RAG回答和可选的直接LLM回答
    """
    if not rag_pipeline or not llm:
        raise HTTPException(status_code=500, detail="系统未初始化")

    try:
        # 使用RAG系统回答
        logger.info(f"处理问题: {query.query}")
        rag_result = rag_pipeline.process(query.query)

        response = {
            "rag_response": {
                "query": rag_result["query"],
                "answer": rag_result["answer"],
                "references": [
                    {
                        "text": doc["text"],
                        "score": doc["score"]
                    }
                    for doc in rag_result["retrieved_documents"]
                ]
            }
        }

        # 如果需要对比，添加直接LLM回答
        if query.compare:
            logger.info("生成直接LLM回答进行对比")
            direct_prompt = f"""你是一个专业的法律顾问。请回答用户的问题。如果不确定答案，请明确说明。请不要编造信息。

用户问题：{query.query}

请给出专业、准确的回答："""
            direct_answer = llm.generate(direct_prompt)

            response["direct_response"] = {
                "answer": direct_answer
            }

        return response

    except Exception as e:
        logger.error(f"问答失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))