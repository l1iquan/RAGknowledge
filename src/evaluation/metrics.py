from typing import List, Dict, Any
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

class RetrievalMetrics:
    """检索评估指标"""
    
    @staticmethod
    def precision_at_k(relevant_docs: List[str], retrieved_docs: List[Dict[str, Any]], k: int) -> float:
        """计算 P@K
        
        Args:
            relevant_docs: 相关文档列表
            retrieved_docs: 检索到的文档列表
            k: 截断位置
        
        Returns:
            P@K 值
        """
        if not retrieved_docs or k <= 0:
            return 0.0
        
        retrieved_texts = [doc["text"] for doc in retrieved_docs[:k]]
        relevant_count = sum(1 for text in retrieved_texts if text in relevant_docs)
        return relevant_count / k

    @staticmethod
    def recall_at_k(relevant_docs: List[str], retrieved_docs: List[Dict[str, Any]], k: int) -> float:
        """计算 R@K
        
        Args:
            relevant_docs: 相关文档列表
            retrieved_docs: 检索到的文档列表
            k: 截断位置
        
        Returns:
            R@K 值
        """
        if not relevant_docs or not retrieved_docs or k <= 0:
            return 0.0
        
        retrieved_texts = [doc["text"] for doc in retrieved_docs[:k]]
        relevant_count = sum(1 for text in retrieved_texts if text in relevant_docs)
        return relevant_count / len(relevant_docs)

class GenerationMetrics:
    """生成评估指标"""
    
    def __init__(self, model_name: str = "moka-ai/m3e-base"):
        """初始化评估器
        
        Args:
            model_name: 用于计算语义相似度的模型名称
        """
        self.model = SentenceTransformer(model_name)
        logger.info(f"加载语义相似度模型：{model_name}")
    
    def semantic_similarity(self, text1: str, text2: str) -> float:
        """计算语义相似度
        
        Args:
            text1: 第一个文本
            text2: 第二个文本
        
        Returns:
            相似度分数
        """
        try:
            # 编码文本
            embedding1 = self.model.encode([text1])[0]
            embedding2 = self.model.encode([text2])[0]
            
            # 计算余弦相似度
            similarity = cosine_similarity(
                embedding1.reshape(1, -1),
                embedding2.reshape(1, -1)
            )[0][0]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"计算语义相似度失败：{str(e)}")
            raise

class RAGMetrics:
    """RAG 系统评估指标"""
    
    def __init__(self):
        """初始化 RAG 评估器"""
        self.retrieval_metrics = RetrievalMetrics()
        self.generation_metrics = GenerationMetrics()
    
    def evaluate_retrieval(self, query_results: List[Dict[str, Any]], ground_truth: Dict[str, List[str]]) -> Dict[str, Any]:
        """评估检索结果
        
        Args:
            query_results: RAG 系统的查询结果列表
            ground_truth: 标准答案，格式为 {query: relevant_docs}
        
        Returns:
            评估指标字典
        """
        metrics = {
            "precision@1": [],
            "precision@3": [],
            "precision@5": [],
            "recall@1": [],
            "recall@3": [],
            "recall@5": []
        }
        
        for result in query_results:
            query = result["query"]
            if query not in ground_truth:
                continue
                
            relevant_docs = ground_truth[query]
            retrieved_docs = result["retrieved_documents"]
            
            # 计算不同 K 值的指标
            for k in [1, 3, 5]:
                p_at_k = self.retrieval_metrics.precision_at_k(relevant_docs, retrieved_docs, k)
                r_at_k = self.retrieval_metrics.recall_at_k(relevant_docs, retrieved_docs, k)
                metrics[f"precision@{k}"].append(p_at_k)
                metrics[f"recall@{k}"].append(r_at_k)
        
        # 计算平均值
        return {
            metric: float(np.mean(values)) if values else 0.0
            for metric, values in metrics.items()
        }
    
    def evaluate_generation(self, query_results: List[Dict[str, Any]], ground_truth: Dict[str, str]) -> Dict[str, Any]:
        """评估生成结果
        
        Args:
            query_results: RAG 系统的查询结果列表
            ground_truth: 标准答案，格式为 {query: answer}
        
        Returns:
            评估指标字典
        """
        similarities = []
        
        for result in query_results:
            query = result["query"]
            if query not in ground_truth:
                continue
                
            generated_answer = result["answer"]
            ground_truth_answer = ground_truth[query]
            
            # 计算生成答案与标准答案的语义相似度
            similarity = self.generation_metrics.semantic_similarity(
                generated_answer,
                ground_truth_answer
            )
            similarities.append(similarity)
        
        return {
            "semantic_similarity": float(np.mean(similarities)) if similarities else 0.0
        }
    
    def evaluate(self, query_results: List[Dict[str, Any]], retrieval_ground_truth: Dict[str, List[str]], generation_ground_truth: Dict[str, str]) -> Dict[str, Any]:
        """评估整个 RAG 系统
        
        Args:
            query_results: RAG 系统的查询结果列表
            retrieval_ground_truth: 检索标准答案
            generation_ground_truth: 生成标准答案
        
        Returns:
            评估指标字典
        """
        retrieval_metrics = self.evaluate_retrieval(query_results, retrieval_ground_truth)
        generation_metrics = self.evaluate_generation(query_results, generation_ground_truth)
        
        # 计算 token 使用统计
        token_stats = {
            "prompt_tokens": [],
            "answer_tokens": [],
            "total_tokens": []
        }
        
        for result in query_results:
            metadata = result["metadata"]
            token_stats["prompt_tokens"].append(metadata["prompt_tokens"])
            token_stats["answer_tokens"].append(metadata["answer_tokens"])
            token_stats["total_tokens"].append(metadata["total_tokens"])
        
        token_metrics = {
            f"{key}_mean": float(np.mean(values)) if values else 0.0
            for key, values in token_stats.items()
        }
        
        return {
            "retrieval_metrics": retrieval_metrics,
            "generation_metrics": generation_metrics,
            "token_metrics": token_metrics
        } 