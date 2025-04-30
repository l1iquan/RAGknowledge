from src.rag.pipeline import RAGPipeline
from src.llm.openai import OpenAILLM
from src.utils.helpers import save_results
import json
import logging
from pathlib import Path

def format_rag_result(result: dict) -> dict:
    """格式化 RAG 结果，添加参考文档信息"""
    return {
        "query": result["query"],
        "answer": result["answer"],
        "references": [
            {
                "text": doc["text"],
                "score": doc["score"]
            }
            for doc in result["retrieved_documents"]
        ]
    }

def main():
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # 初始化 RAG 系统和普通 LLM
    rag_pipeline = RAGPipeline()
    llm = OpenAILLM()
    
    # 测试查询
    test_queries = [
        "在不定期合伙的情况下，一个合伙人突然退出并清偿了其应当承担份额的合伙债务后，是否有权向其他合伙人追偿？",
        "一个公司购买了一台特种设备，该公司应该对这台设备进行哪些管理和维护措施？"
    ]
    
    # 存储结果
    comparison_results = []
    
    for query in test_queries:
        logger.info(f"\n处理查询: {query}")
        
        # 使用 RAG 系统回答
        logger.info("使用 RAG 系统生成回答...")
        rag_result = rag_pipeline.process(query)
        
        # 直接使用 LLM 回答
        logger.info("直接使用 LLM 生成回答...")
        direct_prompt = f"""你是一个专业的法律顾问。请回答用户的问题。如果不确定答案，请明确说明。请不要编造信息。

用户问题：{query}

请给出专业、准确的回答："""
        direct_answer = llm.generate(direct_prompt)
        
        # 添加到比较结果
        comparison = {
            "query": query,
            "rag_response": format_rag_result(rag_result),
            "direct_response": {
                "answer": direct_answer
            }
        }
        comparison_results.append(comparison)
        
        # 打印结果对比
        logger.info("\n=== 结果对比 ===")
        logger.info(f"\n问题: {query}")
        logger.info("\n--- RAG 系统回答 ---")
        logger.info(rag_result["answer"])
        logger.info("\n参考文档:")
        for i, doc in enumerate(rag_result["retrieved_documents"], 1):
            logger.info(f"\n[{i}] 相关度 {doc['score']:.4f}:")
            logger.info(doc["text"])
        logger.info("\n--- 直接 LLM 回答 ---")
        logger.info(direct_answer)
        logger.info("\n" + "="*50)
    
    # 保存结果
    output_dir = Path("test_results")
    output_dir.mkdir(exist_ok=True)
    save_results(comparison_results, output_dir / "comparison_results.json")
    logger.info("\n测试完成，结果已保存到 test_results/comparison_results.json")

if __name__ == "__main__":
    main() 