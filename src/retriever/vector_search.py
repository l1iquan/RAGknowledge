from typing import List, Dict, Any, Optional
from src.config import Config
from src.vectorstore.embeddings import VectorStore
import logging

logger = logging.getLogger(__name__)

class VectorRetriever:
    """向量检索器，用于检索相关文档"""
    
    def __init__(self, config: Optional[Config] = None):
        """初始化向量检索器
        
        Args:
            config: 配置对象，如果为None则创建新的配置对象
        """
        self.config = config or Config()
        self.vector_store = None
        self._initialize_vector_store()
    
    def _initialize_vector_store(self):
        """初始化向量存储"""
        try:
            self.vector_store = VectorStore(self.config.EMBEDDING_MODEL)
            self.vector_store.load(self.config.VECTOR_DB_PATH)
            logger.info("向量存储加载成功")
        except Exception as e:
            logger.error(f"向量存储加载失败: {str(e)}")
            raise
    
    def retrieve(self, query: str, top_k: int = None, min_score: float = None) -> List[Dict[str, Any]]:
        """检索相关文档
        
        Args:
            query: 查询文本
            top_k: 返回的文档数量，如果为None则使用配置中的值
            min_score: 最小相似度阈值，如果为None则使用配置中的值
        
        Returns:
            包含文档内容和相似度分数的字典列表
        """
        if not self.vector_store:
            raise RuntimeError("向量存储未初始化")
        
        top_k = top_k or self.config.TOP_K
        min_score = min_score or self.config.MIN_SIMILARITY_SCORE
        
        try:
            results = self.vector_store.search(
                query=query,
                k=top_k,
                min_score=min_score
            )
            logger.info(f"检索到 {len(results)} 条相关文档")
            return results
        except Exception as e:
            logger.error(f"检索失败: {str(e)}")
            raise
    
    def batch_retrieve(self, queries: List[str], top_k: int = None, min_score: float = None) -> List[List[Dict[str, Any]]]:
        """批量检索相关文档
        
        Args:
            queries: 查询文本列表
            top_k: 每个查询返回的文档数量
            min_score: 最小相似度阈值
        
        Returns:
            每个查询对应的检索结果列表
        """
        return [self.retrieve(query, top_k, min_score) for query in queries] 