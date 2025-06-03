import streamlit as st
import pandas as pd
import requests
import json

faq_df = pd.read_csv("security-faq-bot/faq.csv")

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
        "model": "gpt-3.5-turbo",
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

# チャット履歴用のセッション状態
if "history" not in st.session_state:
    st.session_state["history"] = []

api_key = st.text_input("OpenAIのAPIキー(sk-proj-...)", type="password")
user_q = st.text_input("質問を入力してください（例：未経験でも働けますか？）")

if st.button("送信") and user_q and api_key:
    answer = search_faq(user_q)
    if answer:
        result = f"📚 回答（FAQより）：\n{answer}"
    else:
        st.info("FAQにないのでAIに問い合わせます…")
        gpt_answer = ask_openai(user_q, api_key)
        result = f"🤖 ChatGPTの回答：\n{gpt_answer}"
    # チャット履歴に追加
    st.session_state["history"].append({"user": user_q, "bot": result})

# チャット履歴の表示
st.markdown("### チャット履歴")
for entry in st.session_state["history"]:
    st.markdown(f"**あなた:** {entry['user']}")
    st.markdown(entry["bot"])
    st.markdown("---")
