import streamlit as st
import pandas as pd
import requests
import json

faq_df = pd.read_csv("faq.csv")

def search_faq(user_q):
    for idx, row in faq_df.iterrows():
        if row["質問"] in user_q:
            return row["回答"]
    return None

def ask_openai(user_q, api_key):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "あなたは警備会社の採用担当です。応募希望者に親切かつ丁寧に答えてください。"},
            {"role": "user", "content": user_q}
        ]
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"エラー: {response.status_code} - {response.text}"

st.title("🛡️ 警備会社 求職者向けFAQボット")

api_key = st.text_input("OpenAIのAPIキー(sk-proj-...)", type="password")
user_q = st.text_input("質問を入力してください（例：未経験でも大丈夫ですか？）")

if user_q and api_key:
    answer = search_faq(user_q)
    if answer:
        st.success(f"📚 回答（FAQより）：\n{answer}")
    else:
        st.info("FAQにないのでAIに問い合わせます…")
        gpt_answer = ask_openai(user_q, api_key)
        st.success(f"🤖 ChatGPTの回答：\n{gpt_answer}")
