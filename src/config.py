from pathlib import Path
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

class Config:
    # 基础路径配置
    BASE_DIR = Path(__file__).parent.parent  # 项目根目录
    
    # 文档相关配置
    DATA_DIR = BASE_DIR / "data/documents"
    VECTOR_DIR = BASE_DIR / "data/vectors"
    KNOWLEDGE_BASE = BASE_DIR / "DISC-Law-SFT-Triplet-QA-released.jsonl"
    
    # 文本分块配置
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # 向量存储配置
    EMBEDDING_MODEL = "moka-ai/m3e-base"  # 更换为专门的中文模型
    VECTOR_DB_PATH = VECTOR_DIR / "faiss_index"
    
    # LLM 配置
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # 从环境变量获取
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")  # 从环境变量获取，默认为 gpt-3.5-turbo
    MAX_TOKENS = 2000  # 最大生成 token 数
    TEMPERATURE = 0.7  # 温度参数
    
    # RAG 配置
    TOP_K = 2  # 检索时返回的相关文档数量
    MIN_SIMILARITY_SCORE = 0.5  # 最小相似度阈值
    
    # 评估配置
    METRICS_MODEL = "moka-ai/m3e-base"  # 用于评估的语义相似度模型
    EVAL_OUTPUT_DIR = BASE_DIR / "evaluation/results"  # 评估结果保存目录 