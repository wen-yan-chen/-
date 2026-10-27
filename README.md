# 基于大语言模型与启发式规则的需求歧义检测与修复

![Python](https://img.shields.io/badge/Python-3.14-blue)
![LLM](https://img.shields.io/badge/LLM-DeepSeek-green)
![Architecture](https://img.shields.io/badge/Architecture-Rule%2BLLM-orange)
![Domain](https://img.shields.io/badge/Domain-Requirements-red)

这是一个基于大语言模型（LLM）的软件需求歧义自动化检测与修复小科研实践项目。本项目复现并验证了刘芳（2026）《基于大语言模型的需求歧义检测和修复的方法研究》一文中的核心思想，实现了一个**“启发式规则预筛选 + LLM 推理”**的混合检测架构，以及基于 CoT 的结构化修复框架。

## 项目背景

在现代软件开发中，自然语言编写的需求规格说明书（SRS）极易产生歧义。传统方法泛化能力弱，而单一的大语言模型（LLM）在多阶段推理时容易漏掉局部特征（如拼写错误、模糊词）。本项目通过 14 条精心标注的测试用例，复现了从**“纯 LLM (78.57% 准确率)”**到**“混合架构 (100% 准确率)”**的优化过程。

## 核心特性

*   **六维歧义分类**：支持词汇、句法、语义、语用、语法、语言错误六类歧义检测。
*   **规则+LLM 混合检测**：引入启发式规则（Regex）拦截拼写错误和模糊词，弥补纯 LLM 的漏检问题。
*   **自动化结构化修复**：利用 CoT 提示词，让大模型按照“定位歧义片段 -> 提出可能解释 -> 给出修改建议 -> 阐述理由”的流程进行需求重写。
*   **完整实验数据**：包含手动标注的 `gold_type` 与 LLM 预测的对比，并自动计算准确率。

## 目录结构

```text
├── data.csv                 # 14条测试数据集 (包含需求语句与人工标注的真实标签)
├── run_llm.py               # 基线检测脚本 (纯 LLM 推理)
├── run_llm_new.py           # 进阶检测脚本 (规则拦截 + LLM 推理，附带优先级排序)
├── repair.py                # 需求自动修复脚本 (输出 JSON 格式的修复建议)
├── data_with_llm.csv        # 100% 准确率检测后的完整结果表
├── repair_results_xxx.csv   # 大模型生成的修复建议结果表
└── README.md                # 项目说明文档
```

## 快速开始

### 1. 环境准备

安装所需的 Python 依赖：

```bash
pip install pandas requests
```

### 2. 配置 API Key

本项目默认使用 DeepSeek API（也可替换为 OpenAI 或兼容接口）。

安全提示：请务必使用环境变量，不要在代码中硬编码真实的 API Key！

**Windows (PowerShell):**

```powershell
$env:LLM_API_KEY="sk-你的真实API密钥"
```

**Mac/Linux:**

```bash
export LLM_API_KEY="sk-你的真实API密钥"
```

（在运行代码前，请确保代码中读取的是 `os.getenv("LLM_API_KEY")`，而不是你明文的 Key）

### 3. 运行检测与修复

```bash
# 运行纯 LLM 检测
python run_llm.py

# 运行 规则+LLM 混合检测
python run_llm_new.py

# 运行 需求自动修复
python repair.py
```

## 实验结果

通过引入基于正则表达式的启发式规则拦截，我们成功解决了纯 LLM 在特定语境下的“幻觉”和漏检问题。

| 检测方法 | 准确率 | 错误案例 (漏检) |
| --- | --- | --- |
| 纯 LLM (Few-shot) | 78.57% (11/14) | 漏掉 quickly (模糊词)、systm (拼写错误)、Only (范围不清) |
| 混合架构 (Rule + LLM) | 100.00% (14/14) | 规则成功拦截硬性特征，LLM 专注深层语义推断 |

> 注：LLM 具体表现受模型版本和温度参数 temperature 影响。

## 科研反思与局限（Critical Thinking）

在复现和实验过程中，我们发现了一些非常有意思且值得进一步研究的痛点：

*   **JSON 解析幻觉**：LLM 在修复包含特定标点的需求时，容易输出格式错误的 JSON（如引号未转义），导致程序报错。
*   **过度规范 (Over-specification)**：在修复歧义时，大模型容易“画蛇添足”。例如，将“respond quickly”修改为“within 2 seconds”。虽然消除了模糊性，但引入了原文并未要求的硬性业务指标。
*   **语言漂移**：模型在处理部分英文需求时，修复建议可能会直接返回中文，破坏了需求文档的语言一致性。

## 参考文献

1. 刘芳. (2026). 基于大语言模型的需求歧义检测和修复的方法研究 (硕士学位论文, 东北石油大学).
2. Berry, D. M., Kamsties, E., & Krieger, M. M. (2003). From contract drafting to software specification: Linguistic sources of ambiguity.

## 许可证

本项目采用 MIT License。数据集和代码仅供学习和科研交流使用。
