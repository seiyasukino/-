import streamlit as st
import pandas as pd
import requests
import json

faq_df = pd.read_csv("security-faq-bot-noapi/faq.csv")

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

# スタイリッシュなタイトル・説明文
st.markdown(
    """
    <div style="display: flex; align-items: center;">
        <img src="https://img.icons8.com/color/48/000000/security-checked.png" width="48"/>
        <h1 style='display:inline; color:#1976d2; margin-left:10px;'>警備会社 求職者向けFAQボット</h1>
    </div>
    <div style='color:#555; font-size:16px; margin-bottom:24px;'>
        知りたいことを入力すると、FAQやAIが丁寧にお答えします。
    </div>
    """,
    unsafe_allow_html=True
)

# チャット履歴のセッション状態
if "history" not in st.session_state:
    st.session_state["history"] = []

api_key = st.text_input("OpenAIのAPIキー(sk-proj-...)", type="password")
user_q = st.text_input("💬 質問はこちら", placeholder="例：未経験でも働けますか？")

# 🚀送信ボタンで質問・履歴追加
if st.button("🚀 送信") and user_q and api_key:
    answer = search_faq(user_q)
    if answer:
        result = f"📚 回答（FAQより）：\n{answer}"
    else:
        st.info("FAQにないのでAIに問い合わせます…")
        gpt_answer = ask_openai(user_q, api_key)
        result = f"🤖 ChatGPTの回答：\n{gpt_answer}"
    st.session_state["history"].append({"user": user_q, "bot": result})

st.markdown("### チャット履歴")

for entry in st.session_state["history"]:
    # ユーザー側の吹き出し
    st.markdown(
        f"""
        <div style='display: flex; margin-bottom: 6px;'>
            <div style='background: #e3f2fd; color: #232323; padding: 10px 16px; border-radius: 18px 18px 0 18px; max-width: 70%;'>
                <b>あなた：</b> {entry['user']}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    # ボット側の吹き出し
    st.markdown(
        f"""
        <div style='display: flex; justify-content: flex-end; margin-bottom: 20px;'>
            <div style='background: #fff; color: #232323; padding: 10px 16px; border-radius: 18px 18px 18px 0; max-width: 70%; box-shadow: 1px 1px 8px #ddd;'>
                <b>🤖 ボット：</b> {entry['bot']}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

