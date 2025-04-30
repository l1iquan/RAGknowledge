from typing import List, Dict, Any, Optional
from src.config import Config
from src.retriever.vector_search import VectorRetriever
from src.llm.openai import OpenAILLM
from src.rag.prompt import PromptTemplate
import logging

logger = logging.getLogger(__name__)

class RAGPipeline:
    """RAG 流程实现"""
    
    def __init__(self, config: Optional[Config] = None):
        """初始化 RAG 流程
        
        Args:
            config: 配置对象，如果为None则创建新的配置对象
        """
        self.config = config or Config()
        self.retriever = VectorRetriever(self.config)
        self.llm = OpenAILLM(self.config)
        logger.info("RAG 流程初始化完成")
    
    def process(self, query: str, scoring: bool = False) -> Dict[str, Any]:
        """处理单个查询
        
        Args:
            query: 用户查询
            scoring: 是否需要对文档相关性打分
        
        Returns:
            包含检索结果和生成回答的字典
        """
        try:
            # 检索相关文档
            retrieved_docs = self.retriever.retrieve(
                query=query,
                top_k=self.config.TOP_K,
                min_score=self.config.MIN_SIMILARITY_SCORE
            )
            logger.info(f"检索到 {len(retrieved_docs)} 条相关文档")
            
            # 生成提示词
            prompt = PromptTemplate.generate_prompt(
                query=query,
                documents=retrieved_docs,
                scoring=scoring
            )
            
            # 计算 token 数量
            prompt_tokens = self.llm.count_tokens(prompt)
            logger.info(f"提示词 token 数量：{prompt_tokens}")
            
            # 生成回答
            answer = self.llm.generate(prompt)
            answer_tokens = self.llm.count_tokens(answer)
            logger.info(f"回答 token 数量：{answer_tokens}")
            
            return {
                "query": query,
                "retrieved_documents": retrieved_docs,
                "answer": answer,
                "metadata": {
                    "prompt_tokens": prompt_tokens,
                    "answer_tokens": answer_tokens,
                    "total_tokens": prompt_tokens + answer_tokens
                }
            }
            
        except Exception as e:
            logger.error(f"处理查询失败：{str(e)}")
            raise
    
    def batch_process(self, queries: List[str], scoring: bool = False) -> List[Dict[str, Any]]:
        """批量处理查询
        
        Args:
            queries: 查询列表
            scoring: 是否需要对文档相关性打分
        
        Returns:
            每个查询的处理结果列表
        """
        return [self.process(query, scoring) for query in queries] 