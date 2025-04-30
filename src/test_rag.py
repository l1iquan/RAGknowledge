from src.rag.pipeline import RAGPipeline
from src.evaluation.metrics import RAGMetrics
from src.utils.helpers import save_results
import json
import logging
from pathlib import Path

def main():
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # 初始化 RAG 系统
    pipeline = RAGPipeline()
    
    # 测试查询
    test_queries = [
        "在不定期合伙的情况下，一个合伙人突然退出并清偿了其应当承担份额的合伙债务后，是否有权向其他合伙人追偿？",
        "一个公司购买了一台特种设备，该公司应该对这台设备进行哪些管理和维护措施？"
    ]
    
    # 处理查询
    results = pipeline.batch_process(test_queries, scoring=True)
    
    # 保存结果
    output_dir = Path("test_results")
    output_dir.mkdir(exist_ok=True)
    save_results(results, output_dir / "rag_results.json")
    
    # 评估结果（这里使用示例标准答案）
    metrics = RAGMetrics()
    
    # 示例标准答案（实际使用时需要真实的标准答案）
    retrieval_ground_truth = {
        "在不定期合伙的情况下，一个合伙人突然退出并清偿了其应当承担份额的合伙债务后，是否有权向其他合伙人追偿？": [
            "合伙企业", "债务", "连带责任", "追偿权", "不定期合伙"
        ],
        "一个公司购买了一台特种设备，该公司应该对这台设备进行哪些管理和维护措施？": [
            "特种设备", "安全管理", "维护保养", "定期检验", "使用登记"
        ]
    }
    
    generation_ground_truth = {
        "在不定期合伙的情况下，一个合伙人突然退出并清偿了其应当承担份额的合伙债务后，是否有权向其他合伙人追偿？": 
            "根据《民法典》第九百七十三条规定，合伙人对合伙债务承担连带责任。当一个合伙人突然退出并清偿了其应当承担份额的合伙债务后，依法有权向其他合伙人追偿。",
        
        "一个公司购买了一台特种设备，该公司应该对这台设备进行哪些管理和维护措施？":
            "根据《特种设备安全法》第三十七条，特种设备的使用应具备安全距离和安全防护措施。因此，公司应该确保特种设备周围设有适当的安全距离，并安装相应的安全防护措施。\n\n根据《特种设备安全法》第三十八条，特种设备属于共有的，共有人可以委托物业服务单位或其他管理人管理特种设备。因此，公司应该委托物业服务单位或者其他管理人对特种设备进行管理。\n\n根据《特种设备安全法》第三十九条，特种设备使用单位应对其使用的特种设备进行经常性维护保养和定期自行检查，并作出记录。此外，特种设备使用单位还应定期校验和检修特种设备的安全附件和安全保护装置，并作出记录。\n\n根据《特种设备安全法》第四十条，特种设备使用单位应在检验合格有效期届满前一个月向特种设备检验机构提出定期检验要求。特种设备检验机构接到定期检验要求后，应按照安全技术规范的要求及时进行安全性能检验。特种设备使用单位还应将定期检验标志置于特种设备的显著位置。未经定期检验或检验不合格的特种设备不得继续使用。\n\n综上所述，在购买特种设备后，公司应对特种设备进行以下管理和维护措施：确保设备周围有安全距离和安全防护措施；委托物业服务单位或其他管理人管理特种设备；进行经常性维护保养和定期自行检查，并记录；定期校验和检修特种设备的安全附件和安全保护装置，并记录；在检验合格有效期届满前一个月向特种设备检验机构提出定期检验要求，定期进行安全性能检验并悬挂定期检验标志。"
    }
    
    # 评估
    evaluation_results = metrics.evaluate(
        results,
        retrieval_ground_truth,
        generation_ground_truth
    )
    
    # 保存评估结果
    save_results(evaluation_results, output_dir / "evaluation_results.json")
    logger.info("测试完成，结果已保存到 test_results 目录")

if __name__ == "__main__":
    main() 