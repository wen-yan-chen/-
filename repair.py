import pandas as pd
import requests
import json
import time
import datetime

# 换成你的新 Key
API_KEY = "sk-a41fdc5853c7403d914a68d07f7ec385"

# 读取刚才 100% 准确率的检测结果
df = pd.read_csv("data_with_llm.csv")

REPAIR_PROMPT = """你是一个严谨的软件需求修复专家。
下面这条需求存在【{type}】问题，请按照以下结构进行修复：
1. 找出导致歧义的最小片段（trigger_segment）。
2. 列出可能产生的 2 种不同解释（interpretations）。
3. 给出修改后的清晰、可测试的需求句（suggestion）。
4. 用一句话说明修改理由（reason）。

请严格只输出 JSON 格式，不要输出多余解释。
原始需求：{sentence}

输出格式：
{{
    "trigger_segment": "导致歧义的最小片段",
    "interpretations": ["解释1", "解释2"],
    "suggestion": "修复后的清晰需求句",
    "reason": "为什么这样修改"
}}
"""

def call_repair(sentence, amb_type):
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
    prompt = REPAIR_PROMPT.replace("{type}", amb_type).replace("{sentence}", sentence)
    
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        content = response.json()["choices"][0]["message"]["content"]
        content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        return {"suggestion": "修复失败", "reason": str(e)}

# 只挑出有歧义的句子进行修复
amb_df = df[df["llm_type"] != "无歧义"].copy()
amb_df["trigger_segment"] = ""
amb_df["suggestion"] = ""
amb_df["repair_reason"] = ""

print(f"开始修复 {len(amb_df)} 条歧义需求...\n")

for index, row in amb_df.iterrows():
    print(f"[{index}] 修复: {row['sentence']} ({row['llm_type']})")
    result = call_repair(row['sentence'], row['llm_type'])
    
    amb_df.at[index, "trigger_segment"] = result.get("trigger_segment", "")
    amb_df.at[index, "suggestion"] = result.get("suggestion", "")
    amb_df.at[index, "repair_reason"] = result.get("reason", "")
    
    print(f"  🎯 触发片段: {result.get('trigger_segment')}")
    print(f"  👉 修改建议: {result.get('suggestion')}")
    print(f"  💡 修改理由: {result.get('reason')}\n")
    time.sleep(1)

# 带时间戳保存，防止文件被占用报错
current_time = datetime.datetime.now().strftime("%m%d_%H%M")
output_file = f"repair_results_{current_time}.csv"
amb_df.to_csv(output_file, index=False, encoding="utf-8-sig")

print("="*40)
print(f"🎉 修复完成！结果已保存到 {output_file}")
print("请打开该文件，像需求评审专家一样检查 AI 改得对不对。")