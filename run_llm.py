import pandas as pd
import requests
import json
import time
import os

# ================= 配置区 =================
# 把你刚才复制的 API Key 粘贴到这里（保留引号）
API_KEY = "sk-a41fdc5853c7403d914a68d07f7ec385"
# =========================================

# 读取你的数据
try:
    df = pd.read_csv("data.csv")
except FileNotFoundError:
    print("错误：找不到 data.csv，请确保这个脚本和 data.csv 在同一个文件夹！")
    exit()

# 定义提示词模板
PROMPT_TEMPLATE = """你是一个严谨的软件需求歧义检测专家。请严格只输出 JSON，不要输出任何解释。
请对输入的需求句子进行歧义分类。参考以下定义和示例：

1. 词汇歧义：词语本身有多个含义。
   示例: "The bank can be slippery when wet." (bank指银行还是河岸？)
2. 句法歧义：句子结构或修饰语可以多种解析。
   示例: "The system shall notify the user with the report." (是用report通知，还是通知带report的用户？)
3. 语义歧义：量词、逻辑范围、否定词范围不清。
   示例: "All users must change their password." (是所有用户共用一个，还是每个人改自己的？)
4. 语用歧义：必须依赖上下文，代词或指示词指代不明。
   示例: "The trucks shall treat the roads before they freeze." (they指卡车还是道路？)
5. 语法歧义：被动语态缺主语、词性用错、缺标点。
   示例: "The data process daily." (process词性错误，缺少动词结构)
6. 语言错误歧义：拼写错误、单复数不一致。
   示例: "The systm shall respond quickly." (拼写错误)

【重点判定规则】：
- 如果句子是结构清晰、用词标准的“主-谓-宾”结构，且没有指代不明的代词，必须判定为“无歧义”。
- 仅仅出现 "the" 或 "system" 不构成歧义。

输出格式（严格 JSON）：
{"has_ambiguity": true/false, "type": "词汇歧义/句法歧义/语义歧义/语用歧义/语法歧义/语言错误歧义/无歧义", "confidence": 0到1之间的小数, "reason": "用中文一句话说明原因"}

输入句子：
<SENTENCE>
"""

def call_deepseek(sentence):
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": PROMPT_TEMPLATE.replace("<SENTENCE>", sentence)}
        ],
        "temperature": 0.1 # 温度调低，让输出更稳定
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        
        # 清理 AI 可能带出来的多余 Markdown 标记
        content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        print(f"  请求或解析失败: {e}")
        return {"has_ambiguity": None, "type": "错误", "confidence": 0, "reason": str(e)}

# 准备两个新列
df["llm_type"] = ""
df["llm_conf"] = 0.0
df["llm_reason"] = ""
df["is_correct"] = 0

print(f"开始跑数据，共 {len(df)} 条...\n")

for index, row in df.iterrows():
    sentence = row["sentence"]
    gold = row["gold_type"]
    print(f"[{index+1}/{len(df)}] 正在分析: {sentence[:30]}...")
    
    result = call_deepseek(sentence)
    
    if result.get("type"):
        llm_type = result["type"]
        df.at[index, "llm_type"] = llm_type
        df.at[index, "llm_conf"] = result.get("confidence", 0)
        df.at[index, "llm_reason"] = result.get("reason", "")
        
        # 判断对错
        if llm_type == gold:
            df.at[index, "is_correct"] = 1
            print(f"  ✅ 预测: {llm_type} | 正确")
        else:
            print(f"  ❌ 预测: {llm_type} | 实际: {gold} | 错误")
    
    time.sleep(1) # 停顿1秒，防止请求过快被限流

# 保存结果
output_file = "data_with_llm.csv"
df.to_csv(output_file, index=False, encoding="utf-8-sig")

# 计算准确率
accuracy = df["is_correct"].mean()
print("\n" + "="*30)
print(f"🎉 全部跑完！结果已保存到 {output_file}")
print(f"📊 整体准确率: {accuracy * 100:.2f}%")
print("="*30)