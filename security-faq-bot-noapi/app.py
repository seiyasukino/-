import streamlit as st
import pandas as pd

faq_df = pd.read_csv("faq.csv")

def search_faq(user_q):
    for idx, row in faq_df.iterrows():
        if row["質問"] in user_q:
            return row["回答"]
    return "ごめんなさい、その質問にはまだ答えられません。"

st.title("🛡️ 警備会社 求職者向けFAQボット（APIキー不要）")

user_q = st.text_input("質問を入力してください（例：未経験でも大丈夫ですか？）")

if user_q:
    answer = search_faq(user_q)
    st.success(f"📚 回答：\n{answer}")
