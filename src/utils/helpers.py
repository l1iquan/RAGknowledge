import logging
from typing import List, Dict, Any
from datetime import datetime
import json
import os

logger = logging.getLogger(__name__)

def setup_logging(log_dir: str = "logs", level: int = logging.INFO):
    """设置日志配置
    
    Args:
        log_dir: 日志文件目录
        level: 日志级别
    """
    os.makedirs(log_dir, exist_ok=True)
    
    # 创建日志文件名，包含时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"rag_{timestamp}.log")
    
    # 配置日志格式
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logger.info(f"日志配置完成，日志文件：{log_file}")

def format_retrieval_results(results: List[Dict[str, Any]], include_metadata: bool = False) -> List[Dict[str, Any]]:
    """格式化检索结果
    
    Args:
        results: 检索结果列表
        include_metadata: 是否包含元数据
    
    Returns:
        格式化后的结果列表
    """
    formatted_results = []
    for idx, result in enumerate(results, 1):
        formatted_result = {
            "rank": idx,
            "text": result["text"],
            "score": round(float(result["score"]), 4)
        }
        if include_metadata and "metadata" in result:
            formatted_result["metadata"] = result["metadata"]
        formatted_results.append(formatted_result)
    return formatted_results

def save_results(results: List[Dict[str, Any]], output_file: str):
    """保存结果到文件
    
    Args:
        results: 结果列表
        output_file: 输出文件路径
    """
    try:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        logger.info(f"结果已保存到：{output_file}")
    except Exception as e:
        logger.error(f"保存结果失败：{str(e)}")
        raise

def load_jsonl(file_path: str) -> List[Dict[str, Any]]:
    """加载JSONL文件
    
    Args:
        file_path: JSONL文件路径
    
    Returns:
        数据列表
    """
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                data.append(json.loads(line.strip()))
        logger.info(f"从 {file_path} 加载了 {len(data)} 条数据")
        return data
    except Exception as e:
        logger.error(f"加载JSONL文件失败：{str(e)}")
        raise 