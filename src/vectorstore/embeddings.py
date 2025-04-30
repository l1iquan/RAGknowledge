from typing import List, Optional, Dict, Any
import numpy as np
from pathlib import Path
import faiss
from sentence_transformers import SentenceTransformer
import pickle
from tqdm import tqdm
from src.document_processor.loader import DocumentLoader

class VectorStore:
    def __init__(self, model_name: str):
        print(f"正在加载模型: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.texts = []
    
    def encode_texts(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """将文本批量编码为向量"""
        embeddings = []
        for i in tqdm(range(0, len(texts), batch_size), desc="文本向量化"):
            batch = texts[i:i + batch_size]
            batch_embeddings = self.model.encode(batch, normalize_embeddings=True)  # 添加向量归一化
            embeddings.append(batch_embeddings)
        return np.vstack(embeddings)
    
    def create_index(self, texts: List[str]):
        """创建新的向量索引"""
        print(f"开始处理 {len(texts)} 条文本...")
        self.texts = texts
        
        # 向量化文本
        embeddings = self.encode_texts(texts)
        dimension = embeddings.shape[1]
        
        # 创建FAISS索引（使用余弦相似度）
        self.index = faiss.IndexFlatIP(dimension)  # 内积用于计算余弦相似度
        self.index.add(embeddings.astype('float32'))
        
        print(f"向量索引创建完成，维度: {dimension}")
    
    def save(self, save_dir: Path):
        """保存向量索引和原始文本"""
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存FAISS索引
        faiss.write_index(self.index, str(save_dir / "index.faiss"))
        
        # 保存原始文本
        with open(save_dir / "texts.pkl", "wb") as f:
            pickle.dump(self.texts, f)
        
        print(f"索引和文本已保存到: {save_dir}")
    
    def load(self, save_dir: Path):
        """加载已存在的向量索引和原始文本"""
        print(f"从 {save_dir} 加载索引和文本...")
        
        # 加载FAISS索引
        self.index = faiss.read_index(str(save_dir / "index.faiss"))
        
        # 加载原始文本
        with open(save_dir / "texts.pkl", "rb") as f:
            self.texts = pickle.load(f)
        
        print(f"加载完成，共有 {len(self.texts)} 条文本")
    
    def enhance_query(self, query: str) -> str:
        """增强查询文本"""
        # 预处理查询文本
        query = DocumentLoader.preprocess_text(query)
        return query
    
    def search(self, query: str, k: int = 3, min_score: float = 0.5) -> List[Dict[str, Any]]:
        """搜索最相似的文档
        
        Args:
            query: 查询文本
            k: 返回的结果数量
            min_score: 最小相似度阈值，低于此值的结果将被过滤
        
        Returns:
            包含文本内容和相似度分数的字典列表
        """
        # 增强查询
        enhanced_query = self.enhance_query(query)
        
        # 编码查询文本
        query_vector = self.model.encode([enhanced_query], normalize_embeddings=True)
        query_vector = np.squeeze(query_vector)  # 移除多余的维度
        
        # 获取更多候选结果用于后处理
        k_candidates = min(k * 3, 10)
        distances, indices = self.index.search(query_vector.reshape(1, -1).astype('float32'), k_candidates)
        
        # 处理结果
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            # 由于使用内积，距离就是余弦相似度（向量已归一化）
            score = float(dist)
            
            if score >= min_score:
                results.append({
                    "text": self.texts[idx],
                    "score": score,
                    "index": int(idx)
                })
        
        # 按相似度排序并返回前k个结果
        results = sorted(results, key=lambda x: x['score'], reverse=True)[:k]
        
        return results 