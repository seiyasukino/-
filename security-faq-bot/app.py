import streamlit as st
import pandas as pd
import requests
import json

faq_df = pd.read_csv("faq.csv")

# 背景グラデーション
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(120deg, #e0eafc 0%, #cfdef3 100%);
    }
    </style>
""", unsafe_allow_html=True)

# 送信ボタンの色
st.markdown("""
    <style>
    div.stButton > button {
        background-color: #ff6f61;
        color: white;
        border-radius: 12px;
        font-size: 1.2rem;
        padding: 10px 24px;
        border: none;
        transition: background 0.2s;
    }
    div.stButton > button:hover {
        background-color: #e53935;
        color: #fff;
    }
    </style>
""", unsafe_allow_html=True)

# サイドバー
with st.sidebar:
    st.markdown("### 👀 よくある質問例")
    for idx, row in faq_df.iterrows():
        st.write(f"・{row['質問']}")
    st.markdown("---")
    st.write("🚩 サポート: support@example.com")

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

st.markdown("---")
with st.expander("▼ よくある質問リストを見る"):
    for idx, row in faq_df.iterrows():
        st.write(f"Q. {row['質問']}")
        st.write(f"A. {row['回答']}")
        st.markdown("---")

# チャット履歴のセッション状態
if "history" not in st.session_state:
    st.session_state["history"] = []

# フォーム（Enterキー送信対応）
with st.form("qa_form", clear_on_submit=True):
    api_key = st.text_input("OpenAIのAPIキー(sk-proj-...)", type="password")
    user_q = st.text_input("💬 質問はこちら", placeholder="例：未経験でも働けますか？")
    st.caption("※ 質問はできるだけ具体的に入力すると正確な答えが得られます")
    submitted = st.form_submit_button("🚀 送信")

if submitted and user_q and api_key:
    answer = search_faq(user_q)
    if answer:
        result = answer  # 🤖は履歴には付けず
    else:
        st.info("FAQにないのでAIに問い合わせます…")
        with st.spinner("AIが考え中です..."):
            gpt_answer = ask_openai(user_q, api_key)
        result = gpt_answer
    st.session_state["history"].append({"user": user_q, "bot": result})

st.markdown("### チャット履歴")

for entry in st.session_state["history"]:
    # ユーザーの吹き出し
    st.markdown(
        f"""
        <div style='display: flex; margin-bottom: 10px;'>
            <div style='background: #e3f2fd; color: #232323; padding: 15px 22px; border-radius: 22px 22px 0 22px; max-width: 60%; box-shadow: 0 2px 8px #d7eafc; font-size: 1.08rem;'>
                <b>あなた：</b> {entry['user']}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    # ボットの吹き出し（ここでだけ🤖をつける！）
    st.markdown(
        f"""
        <div style='display: flex; justify-content: flex-end; margin-bottom: 34px;'>
            <div style='background: #fff; color: #232323; padding: 15px 22px; border-radius: 22px 22px 22px 0; max-width: 60%; box-shadow: 0 2px 12px #e0e0e0; font-size: 1.08rem;'>
                <b style="color:#1976d2;">🤖：</b> {entry['bot']}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
