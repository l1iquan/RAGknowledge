from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from src.retriever.vector_search import VectorRetriever
from src.utils.helpers import format_retrieval_results
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="法律文档检索系统",
    description="基于向量检索的法律文档检索系统API",
    version="1.0.0"
)

# 初始化检索器
retriever = None

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
    """应用启动时初始化检索器"""
    global retriever
    try:
        retriever = VectorRetriever()
        logger.info("检索器初始化成功")
    except Exception as e:
        logger.error(f"检索器初始化失败: {str(e)}")
        raise

@app.get("/")
async def root():
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