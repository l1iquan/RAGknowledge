from typing import List, Dict, Any
from string import Template

class PromptTemplate:
    """提示词模板"""
    
    # 基础提示词模板
    BASE_TEMPLATE = Template("""你是一个专业的法律顾问。请根据以下参考文档回答用户的问题。
如果无法从参考文档中找到答案，请明确说明。请不要编造信息。

参考文档：
${context}

用户问题：${query}

请给出专业、准确的回答：""")
    
    # 带评分的提示词模板
    SCORING_TEMPLATE = Template("""你是一个专业的法律顾问。请根据以下参考文档回答用户的问题，并为每个参考文档的相关性打分。
如果无法从参考文档中找到答案，请明确说明。请不要编造信息。

参考文档：
${context}

用户问题：${query}

请先为每个参考文档的相关性打分（0-10分），然后给出专业、准确的回答：""")
    
    @staticmethod
    def format_context(documents: List[Dict[str, Any]]) -> str:
        """格式化上下文文档
        
        Args:
            documents: 文档列表，每个文档包含text和score字段
        
        Returns:
            格式化后的上下文字符串
        """
        context_parts = []
        for idx, doc in enumerate(documents, 1):
            score = round(float(doc["score"]), 4)
            context_parts.append(f"[{idx}] 相关度 {score}：\n{doc['text']}\n")
        return "\n".join(context_parts)
    
    @classmethod
    def generate_prompt(cls, query: str, documents: List[Dict[str, Any]], scoring: bool = False) -> str:
        """生成提示词
        
        Args:
            query: 用户查询
            documents: 相关文档列表
            scoring: 是否需要对文档相关性打分
        
        Returns:
            生成的提示词
        """
        context = cls.format_context(documents)
        template = cls.SCORING_TEMPLATE if scoring else cls.BASE_TEMPLATE
        return template.substitute(context=context, query=query) 