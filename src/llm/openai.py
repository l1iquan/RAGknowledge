from typing import List, Dict, Any, Optional
import openai
from src.llm.base import BaseLLM
from src.config import Config
import tiktoken
import logging

logger = logging.getLogger(__name__)

class OpenAILLM(BaseLLM):
    """OpenAI LLM 实现"""
    
    def __init__(self, config: Optional[Config] = None):
        """初始化 OpenAI LLM
        
        Args:
            config: 配置对象，如果为None则创建新的配置对象
        """
        self.config = config or Config()
        self.model = self.config.LLM_MODEL
        
        # 尝试获取模型对应的编码器
        try:
            self.encoding = tiktoken.encoding_for_model(self.model)
            logger.info(f"成功加载模型 {self.model} 的编码器")
        except KeyError:
            # 如果模型不被支持，使用 cl100k_base 编码器（GPT-4 和 GPT-3.5-turbo 使用的编码器）
            logger.warning(f"模型 {self.model} 没有对应的编码器，使用默认编码器 cl100k_base")
            self.encoding = tiktoken.get_encoding("cl100k_base")
        
        # 设置 OpenAI API Key
        openai.api_key = self.config.OPENAI_API_KEY
        if not openai.api_key:
            logger.error("未设置 OPENAI_API_KEY 环境变量")
            raise ValueError("未设置 OPENAI_API_KEY 环境变量，请在 .env 文件中设置")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """生成回复
        
        Args:
            prompt: 提示词
            **kwargs: 其他参数，可以包括：
                temperature: 温度参数
                max_tokens: 最大生成 token 数
                stop: 停止生成的标记
        
        Returns:
            生成的回复文本
        """
        try:
            # 设置默认参数
            params = {
                "model": self.model,
                "temperature": kwargs.get("temperature", self.config.TEMPERATURE),
                "max_tokens": kwargs.get("max_tokens", self.config.MAX_TOKENS),
            }
            
            # 添加可选参数
            if "stop" in kwargs:
                params["stop"] = kwargs["stop"]
            
            # 调用 API
            response = openai.ChatCompletion.create(
                messages=[{"role": "user", "content": prompt}],
                **params
            )
            
            # 提取回复文本
            reply = response.choices[0].message.content.strip()
            logger.info(f"生成回复成功，长度：{len(reply)}")
            return reply
            
        except Exception as e:
            logger.error(f"生成回复失败：{str(e)}")
            raise
    
    def batch_generate(self, prompts: List[str], **kwargs) -> List[str]:
        """批量生成回复
        
        Args:
            prompts: 提示词列表
            **kwargs: 其他参数
        
        Returns:
            生成的回复文本列表
        """
        return [self.generate(prompt, **kwargs) for prompt in prompts]
    
    def count_tokens(self, text: str) -> int:
        """计算文本的 token 数量
        
        Args:
            text: 输入文本
        
        Returns:
            token 数量
        """
        return len(self.encoding.encode(text)) 