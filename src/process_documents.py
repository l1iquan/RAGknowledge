import sys
from pathlib import Path
import os

# 添加src目录到Python路径
current_dir = Path(__file__).parent.parent
sys.path.append(str(current_dir))

from src.document_processor.loader import DocumentLoader
from src.vectorstore.embeddings import VectorStore
from src.config import Config

def main():
    # 初始化配置
    config = Config()
    
    print("1. 加载文档...")
    loader = DocumentLoader(config.KNOWLEDGE_BASE)
    texts = loader.get_texts()
    print(f"加载了 {len(texts)} 个文档")
    
    # 打印前两个文档的内容作为示例
    print("\n示例文档内容:")
    for i, text in enumerate(texts[:2]):
        print(f"\n--- 文档 {i+1} ---")
        print(text[:500] + "..." if len(text) > 500 else text)
    
    print("\n2. 创建向量索引...")
    vector_store = VectorStore(config.EMBEDDING_MODEL)
    vector_store.create_index(texts)
    
    print("\n3. 保存向量索引...")
    os.makedirs(config.VECTOR_DB_PATH, exist_ok=True)
    vector_store.save(config.VECTOR_DB_PATH)
    print(f"向量索引已保存到: {config.VECTOR_DB_PATH}")
    
    # 测试搜索
    print("\n4. 测试搜索...")
    test_queries = [
        "什么是民事诉讼？",
        "行政诉讼中被告的举证责任是什么？",
        "合伙企业的债务承担方式是什么？"
    ]
    
    for query in test_queries:
        print(f"\n查询: {query}")
        print("-" * 50)
        results = vector_store.search(query, k=2)
        
        for i, result in enumerate(results, 1):
            print(f"\n结果 {i} (相似度得分: {result['score']:.4f}):")
            print(result['text'][:500] + "..." if len(result['text']) > 500 else result['text'])

if __name__ == "__main__":
    main() 