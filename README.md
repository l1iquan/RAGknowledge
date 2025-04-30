# RAG 知识库问答系统

这是一个基于 RAG (Retrieval Augmented Generation) 的知识库问答系统，专门针对法律领域的问答场景设计。系统采用先进的向量检索和大语言模型技术，实现了高效精准的法律知识问答。

## 💡 系统特点

- **专业领域设计**：基于法律问答数据集构建，专门针对法律领域的问答需求
- **高效检索**：使用 FAISS 向量数据库，支持快速、高效的相似文档检索
- **智能问答**：集成 OpenAI GPT 模型，提供准确、连贯的回答
- **可扩展架构**：模块化设计，易于扩展和维护
- **全面评估**：内置评估模块，支持系统性能的量化评估

## 🔍 系统架构

```
rag_project/
├── data/                      # 数据存储目录
│   ├── documents/            # 原始文档存储
│   └── vectors/             # 向量数据存储
│       └── faiss_index/    # FAISS 向量索引
├── src/                      # 源代码目录
│   ├── api/                 # API 接口模块
│   ├── document_processor/  # 文档处理模块
│   ├── vectorstore/        # 向量存储模块
│   ├── retriever/          # 检索模块
│   ├── llm/                # LLM 集成模块
│   ├── rag/                # RAG 核心实现
│   ├── evaluation/         # 评估模块
│   └── utils/              # 工具函数
└── test_results/           # 测试结果目录
```

## 🛠️ 核心模块说明

### 1. 文档处理模块 (document_processor)
- 负责原始文档的加载和预处理
- 支持文本分块，确保检索粒度合适
- 处理各种格式的输入文档

### 2. 向量存储模块 (vectorstore)
- 使用 m3e-base 模型进行文本向量化
- 采用 FAISS 进行高效的向量存储和检索
- 支持增量更新和持久化存储

### 3. 检索模块 (retriever)
- 实现基于语义的相似文档检索
- 支持 Top-K 检索和相似度阈值过滤
- 提供批量检索能力

### 4. LLM 模块 (llm)
- 集成 OpenAI GPT 模型
- 支持参数化配置（温度、最大 token 等）
- 实现 token 计数和成本控制

### 5. RAG 核心实现 (rag)
- 统一的 RAG 处理管道
- 智能提示词模板管理
- 结果格式化和后处理

### 6. 评估模块 (evaluation)
- 支持多维度的系统评估
- 提供详细的评估指标
- 结果可视化和报告生成

## 📦 安装指南

1. 克隆项目并创建虚拟环境：
```bash
git clone [项目地址]
cd rag_project
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. 安装依赖：
```bash
pip install -r requirements.txt   (可能不全，后期缺啥安啥)
```

3. 环境配置：
- 在项目根目录创建 .env 文件
- 设置必要的环境变量：
```
OPENAI_API_KEY=你的OpenAI API密钥
LLM_MODEL=gpt-3.5-turbo  # 或其他支持的模型
```

## 🚀 使用指南

### 1. 数据准备
```bash
# 处理文档并创建向量索引
python src/process_documents.py   （文档太大向量化比较慢，可以用部分文档测试）
```

### 2. 启动服务
```bash
# 启动 API 服务
python src/main.py （可以进行向量查询，没有其他的作用）
```

### 3. 系统评估
```bash
# 运行评估脚本
python src/test_rag.py （这个测试不全，没有大模型直接回答的结果，运行结果为test_results/rag_results.json）

python src/test_compare.py  （这个测试全，包含大模型直接回答的结果，运行结果为test_results/rag_results.json）

```

## ⚙️ 关键配置说明

配置文件位于 `src/config.py`，主要包含：

- **文档处理配置**
  - CHUNK_SIZE：文档分块大小（默认1000）
  - CHUNK_OVERLAP：分块重叠长度（默认200）

- **向量存储配置**
  - EMBEDDING_MODEL：使用的向量模型
  - VECTOR_DB_PATH：向量数据库存储路径

- **LLM 配置**
  - LLM_MODEL：使用的语言模型
  - MAX_TOKENS：最大生成 token 数
  - TEMPERATURE：生成温度参数

- **RAG 配置**
  - TOP_K：检索文档数量
  - MIN_SIMILARITY_SCORE：最小相似度阈值

## 📊 性能指标

系统评估结果存储在 test_results 目录下：
- comparison_results.json：对比测试结果
- evaluation_results.json：整体评估结果
- rag_results.json：RAG 系统测试结果
- search_results.json：检索模块测试结果

## 📝 注意事项

1. 向量化过程可能需要较长时间，建议使用 GPU 加速
2. 请确保有足够的磁盘空间存储向量索引
3. API 密钥请妥善保管，不要提交到代码仓库
4. 建议在生产环境中使用负载均衡和错误处理

## 🔄 开发计划

- [x] 基础文档处理和向量化
- [x] 实现检索模块
- [x] 集成 LLM
- [x] 完整 RAG 流程
- [x] 评估和优化
- [ ] 支持更多文档格式
- [ ] 优化提示词模板
- [ ] 增加缓存机制
- [ ] 改进评估指标

## 🤝 贡献指南

欢迎贡献代码或提出建议！请确保在提交 PR 前：
1. 运行所有测试确保通过
2. 更新相关文档
3. 遵循项目的代码规范

## 📄 许可证

本项目采用 MIT 许可证
