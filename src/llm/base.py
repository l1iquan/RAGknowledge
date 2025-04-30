from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseLLM(ABC):
    """LLM 基础接口类"""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """生成回复
        
        Args:
            prompt: 提示词
            **kwargs: 其他参数
        
        Returns:
            生成的回复文本
        """
        pass
    
    @abstractmethod
    def batch_generate(self, prompts: List[str], **kwargs) -> List[str]:
        """批量生成回复
        
        Args:
            prompts: 提示词列表
            **kwargs: 其他参数
        
        Returns:
            生成的回复文本列表
        """
        pass
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """计算文本的 token 数量
        
        Args:
            text: 输入文本
        
        Returns:
            token 数量
        """
        pass 