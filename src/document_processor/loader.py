import jsonlines
import re
from typing import List, Dict
from pathlib import Path
from dataclasses import dataclass

@dataclass
class Document:
    input: str
    output: str
    reference: List[str]
    id: str

class DocumentLoader:
    def __init__(self, file_path: Path):
        self.file_path = file_path
    
    @staticmethod
    def preprocess_text(text: str) -> str:
        """文本预处理
        1. 标准化标点符号
        2. 移除多余空格
        3. 清理特殊字符
        """
        # 标准化标点符号
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        text = text.replace('【', '[').replace('】', ']')
        text = text.replace('（', '(').replace('）', ')')
        
        # 移除多余空格
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 标准化换行符
        text = text.replace('\n\n', '\n')
        
        return text
    
    @staticmethod
    def format_references(references: List[str]) -> str:
        """格式化参考文献"""
        if not references:
            return ""
        
        formatted_refs = []
        for i, ref in enumerate(references, 1):
            # 提取法律名称和具体条款
            ref = DocumentLoader.preprocess_text(ref)
            formatted_refs.append(f"{i}. {ref}")
        
        return "\n".join(formatted_refs)
    
    def load_documents(self) -> List[Document]:
        """加载JSONL文件并转换为Document对象列表"""
        documents = []
        with jsonlines.open(self.file_path) as reader:
            for item in reader:
                doc = Document(
                    input=self.preprocess_text(item.get("input", "")),
                    output=self.preprocess_text(item.get("output", "")),
                    reference=item.get("reference", []),
                    id=item.get("id", "")
                )
                documents.append(doc)
        return documents
    
    def get_texts(self) -> List[str]:
        """获取所有文档的文本表示，用于向量化
        
        返回格式:
        问题：...
        答案：...
        法律依据：
        1. 法律条款1
        2. 法律条款2
        ...
        """
        documents = self.load_documents()
        texts = []
        
        for doc in documents:
            # 格式化参考文献
            references = self.format_references(doc.reference)
            
            # 组合最终文本
            text_parts = [
                f"问题：{doc.input}",
                f"答案：{doc.output}"
            ]
            
            if references:
                text_parts.append(f"法律依据：\n{references}")
            
            # 使用双换行符连接各部分
            text = "\n\n".join(text_parts)
            texts.append(text)
        
        return texts 