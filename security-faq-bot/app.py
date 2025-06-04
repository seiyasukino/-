import streamlit as st
import pandas as pd
import requests
import json
import difflib

faq_df = pd.read_csv("faq.csv")

st.markdown("""
    <style>
    body { background: #f0f4fa !important; }
    .main-card {
        background: #f6fafd;
        border-radius: 28px;
        box-shadow: 0 8px 32px 0 rgba(44, 101, 144, 0.09), 0 1.5px 8px #d7eafc;
        padding: 42px 36px 28px 36px;
        max-width: 540px;
        margin: 40px auto 32px auto;
        border: none;
        border-top: 4px solid #1976d2;
        border-bottom: 4px solid #00c7b1;
        transition: box-shadow 0.3s, background 0.3s;
    }
    .stTextInput > div > div > input {
        background: #e3f2fd;
        border-radius: 16px;
        border: 1.5px solid #1976d2;
        font-size: 1.13rem;
        padding: 14px 18px;
        margin-bottom: 10px;
    }
    div.stButton > button {
        background-color: #00c7b1;
        color: white;
        border-radius: 14px;
        font-size: 1.13rem;
        padding: 11px 32px;
        border: none;
        transition: background 0.2s;
        box-shadow: 0 2px 8px #c8f2e7;
    }
    div.stButton > button:hover {
        background-color: #1976d2;
        color: #fff;
    }
    .chat-container {
        margin: 28px 0 0 0;
    }
    @keyframes fadeInUp {
        0% { opacity: 0; transform: translateY(20px);}
        100% { opacity: 1; transform: translateY(0);}
    }
    .user-bubble, .bot-bubble {
        animation: fadeInUp 0.7s;
    }
    .user-row { display: flex; align-items: center; margin-bottom: 10px; }
    .bot-row { display: flex; align-items: center; justify-content: flex-end; margin-bottom: 22px;}
    .user-icon, .bot-icon {
        width: 28px; height: 28px; border-radius: 50%; margin: 0 8px 0 0;
        background: #e0eafc; display: flex; align-items: center; justify-content: center;
        font-size: 1.3rem;
    }
    .user-bubble {
        background: #1976d2;
        color: white;
        padding: 13px 20px;
        border-radius: 22px 22px 6px 22px;
        max-width: 70%;
        font-size: 1.08rem;
        box-shadow: 0 1px 8px #b3c9e7;
        margin-left: 0;
        margin-right: auto;
    }
    .bot-bubble {
        background: #f3f6fb;
        color: #232323;
        padding: 13px 20px;
        border-radius: 22px 22px 22px 6px;
        max-width: 70%;
        font-size: 1.08rem;
        box-shadow: 0 2px 8px #e0e0e0;
        margin-left: auto;
        margin-right: 0;
    }
    @media (max-width: 700px) {
        .main-card, .chat-container { max-width: 98vw !important; padding: 8vw 2vw 8vw 2vw !important; }
        .user-bubble, .bot-bubble { max-width: 90vw !important; font-size: 1rem !important;}
    }
    </style>
""", unsafe_allow_html=True)


# --- CSSはそのまま ---

# タイトル・説明（カードの外！）
col1, col2 = st.columns([1, 7])
with col1:
    st.image("guard_icon.png", width=48)
with col2:
    st.markdown(
        """
        <h2 style='color:#1976d2; margin-bottom:0px;'>警備会社 <span style="color:#00c7b1;">求職者向けFAQチャット</span></h2>
        <div style='color:#555; font-size:15px; margin-bottom:22px; font-weight:400;'>
            ITで採用をもっと身近に。FAQやAIがあなたの疑問にすぐ答えます。
        </div>
        """, unsafe_allow_html=True)

# キャラクター選択（カードの外！）
character = st.selectbox(
    "キャラクターを選んでね",
    ["警備くん（やさしい）", "ロボット（ユーモア）", "けいびにゃん（かわいい）"]
)
if character == "警備くん（やさしい）":
    system_msg = "あなたは警備会社のマスコット「警備くん」です。語尾は『〜ですよ』『〜ますね』など、やさしく親しみやすい口調で答えてください。"
    bot_label = "<b style='color:#1976d2;'>🧑‍✈️ 警備くん：</b>"
    bot_icon = "🧑‍✈️"
elif character == "ロボット（ユーモア）":
    system_msg = "あなたは警備会社のロボット案内係『セキュリティボット』です。語尾に『〜であります』『〜なのだ』をつけて、親切でユーモラスに答えてください。"
    bot_label = "<b style='color:#1976d2;'>🤖 ロボット：</b>"
    bot_icon = "🤖"
else:
    system_msg = "あなたは警備会社の猫型AI『けいびにゃん』です。FAQの内容を変えず、語尾だけ『〜にゃ』『〜だよ♪』にして、かわいく答えてください。"
    bot_label = "<b style='color:#b388ff;'>🐱 けいびにゃん：</b>"
    bot_icon = "🐱"

col3, col4 = st.columns([1, 7])
with col3:
    st.image("guard_icon.png", width=36)
with col4:
    st.markdown(
        "<span style='font-size:1.12rem; color:#1976d2; font-weight:bold;'>警備くん：質問はこちら</span>",
        unsafe_allow_html=True)

# ===== ここからカードで囲む =====
st.markdown('<div class="main-card">', unsafe_allow_html=True)

# 入力・送信フォーム
with st.form("chat_form", clear_on_submit=True):
    api_key = st.text_input("OpenAIのAPIキー(sk-proj-...)", type="password")
    user_q = st.text_input("", placeholder="お気軽にご相談ください😊 例：未経験でも働けますか？")
    submitted = st.form_submit_button("✈️ 送信")

if "history" not in st.session_state:
    st.session_state["history"] = []

def ask_openai(user_q, api_key, system_msg):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_q}
        ]
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"エラー: {response.status_code} - {response.text}"

def search_faq(user_q):
    questions = faq_df["質問"].tolist()
    for idx, row in faq_df.iterrows():
        if row["質問"] == user_q:
            return row["回答"]
    for idx, row in faq_df.iterrows():
        if row["質問"] in user_q or user_q in row["質問"]:
            return row["回答"]
    matches = difflib.get_close_matches(user_q, questions, n=1, cutoff=0.5)
    if matches:
        return faq_df[faq_df["質問"] == matches[0]]["回答"].values[0]
    return None

if submitted and user_q:
    answer = search_faq(user_q)
    if answer:
        with st.spinner("AIがキャラクター口調でお答え中です..."):
            bot_msg = ask_openai(answer, api_key, system_msg)
    else:
        with st.spinner("AIが考え中です..."):
            bot_msg = ask_openai(user_q, api_key, system_msg)
    st.session_state["history"].append({"user": user_q, "bot": bot_msg})

# チャット履歴（アニメーション・レスポンシブ・アイコン切替つき）
if st.session_state["history"]:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for entry in st.session_state["history"]:
        # ユーザー
        st.markdown(
            f"""
            <div class="user-row">
                <div class="user-icon">🧑</div>
                <div class="user-bubble"><b>あなた：</b> {entry['user']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        # ボット
        st.markdown(
            f"""
            <div class="bot-row">
                <div class="bot-bubble">{bot_label} {entry['bot']}</div>
                <div class="bot-icon">{bot_icon}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

# メインカード終了
st.markdown('</div>', unsafe_allow_html=True)
