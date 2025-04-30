from vectorstore.embeddings import VectorStore
from config import Config
import json
import os
from typing import List, Dict, Any

def evaluate_results(results: List[Dict[str, Any]], expected_keywords: List[str]) -> Dict[str, Any]:
    """
    评估搜索结果的质量
    
    Args:
        results: 搜索结果列表
        expected_keywords: 预期关键词列表
    
    Returns:
        包含评估指标的字典
    """
    total_matches = 0
    keyword_matches = {keyword: 0 for keyword in expected_keywords}
    
    for result in results:
        text = result["text"].lower()
        for keyword in expected_keywords:
            if keyword.lower() in text:
                keyword_matches[keyword] += 1
                total_matches += 1
    
    coverage = len([k for k, v in keyword_matches.items() if v > 0]) / len(expected_keywords)
    
    return {
        "total_matches": total_matches,
        "keyword_matches": keyword_matches,
        "coverage": coverage
    }

def test_search():
    """
    测试搜索功能
    """
    # 初始化配置和向量存储
    config = Config()
    vector_store = VectorStore(config.EMBEDDING_MODEL)
    
    # 检查向量存储目录是否存在
    if not os.path.exists(config.VECTOR_DB_PATH):
        raise FileNotFoundError(f"向量索引目录不存在: {config.VECTOR_DB_PATH}")
    
    # 加载向量索引
    vector_store.load(config.VECTOR_DB_PATH)
    
    # 测试用例
    test_cases = [
        {
            "query": "某基金管理人未按规定召集基金份额持有人大会，导致未能及时解决投资者的疑虑和问题，该如何处理？",
            "expected_keywords": ["基金管理人", "基金份额持有人大会", "投资者疑虑", "问题处理"]
        }
    ]
    
    # 创建测试结果目录
    os.makedirs("test_results", exist_ok=True)
    
    all_results = []
    
    # 运行测试用例
    for case in test_cases:
        print(f"\n测试查询: {case['query']}")
        print("-" * 50)
        
        results = vector_store.search(case["query"], k=1)  # 修改参数名从 top_k 为 k
        evaluation = evaluate_results(results, case["expected_keywords"])
        
        print(f"预期关键词: {', '.join(case['expected_keywords'])}")
        print(f"关键词匹配总数: {evaluation['total_matches']}")
        print(f"关键词覆盖率: {evaluation['coverage']:.2%}")
        print("\n搜索结果:")
        
        for i, result in enumerate(results, 1):
            text = result["text"][:300] + "..." if len(result["text"]) > 300 else result["text"]
            print(f"\n{i}. 相似度: {result['score']:.4f}")
            print(f"文本: {text}")
        
        case_result = {
            "query": case["query"],
            "expected_keywords": case["expected_keywords"],
            "evaluation": evaluation,
            "results": results
        }
        all_results.append(case_result)
    
    # 保存测试结果
    with open("test_results/search_results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print("\n测试结果已保存到 test_results/search_results.json")

if __name__ == "__main__":
    test_search() 