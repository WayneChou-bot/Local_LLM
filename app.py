import streamlit as st
from private_gpt import load_llm, get_answer
from PIL import Image
import os

st.set_page_config(page_title="企業內部 ChatGPT 問答系統", layout="wide")

# 頂部 Logo 與標題
col1, col2 = st.columns([1, 5])
with col1:
    logo = Image.open("logo.png") if os.path.exists("logo.png") else None
    if logo:
        st.image(logo, width=80)
with col2:
    st.title("🏢 企業內部 ChatGPT 問答系統")
    st.caption("整合私有資料，實現智慧問答 Copilot")

# 輸入問題
query = st.text_input("請輸入你的問題：", placeholder="例如：我們的產品保固期多久？")

# 啟動問答流程
if query:
    with st.spinner("AI 正在分析文件與回答..."):
        llm = load_llm()
        response, sources = get_answer(query, llm)

    st.markdown("---")
    st.subheader("📣 回答內容")
    st.markdown(response)

    if sources:
        st.subheader("📄 資料來源")
        for i, doc in enumerate(sources):
            metadata = doc.metadata if hasattr(doc, 'metadata') else {}
            name = metadata.get("source", f"文件{i+1}")
            st.markdown(f"- `{name}`")
