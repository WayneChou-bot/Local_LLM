import streamlit as st
import os
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

VECTOR_DIR = "vectorstore"
SOURCE_DIR = "source_documents"

def load_single_document(filepath):
    if filepath.endswith(".pdf"):
        loader = PyMuPDFLoader(filepath)
    elif filepath.endswith(".txt"):
        loader = TextLoader(filepath)
    elif filepath.endswith(".docx"):
        loader = Docx2txtLoader(filepath)
    else:
        raise ValueError("Unsupported file type")
    return loader.load()

def ingest_all():
    st.info("📄 開始處理文件資料夾...")
    
    if not os.path.exists(SOURCE_DIR):
        st.error("❌ 找不到資料夾 source_documents")
        return

    documents = []
    for filename in os.listdir(SOURCE_DIR):
        filepath = os.path.join(SOURCE_DIR, filename)
        if filename.lower().endswith((".pdf", ".txt", ".docx")):
            st.write(f"📂 載入：{filename}")
            documents.extend(load_single_document(filepath))

    if not documents:
        st.warning("⚠️ 未找到任何可處理文件。")
        return

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings()

    if os.path.exists(f"{VECTOR_DIR}/index.faiss"):
        db = FAISS.load_local(VECTOR_DIR, embeddings, allow_dangerous_deserialization=True)
        db.add_documents(texts)
        st.success(f"✅ 已新增 {len(texts)} 筆段落到現有向量資料庫。")
    else:
        db = FAISS.from_documents(texts, embeddings)
        db.save_local(VECTOR_DIR)
        st.success(f"✅ 向量資料庫建立完成，共 {len(texts)} 筆段落。")

# ------------------------
# Streamlit UI
# ------------------------
st.set_page_config(page_title="文件向量化", layout="centered")
st.title("📚 文件向量化工具")

st.markdown("請上傳文件至 `source_documents/` 資料夾後，點擊下方按鈕進行處理。")

if st.button("🚀 一鍵執行 ingest"):
    ingest_all()

# 顯示當前已有的文件
if os.path.exists(SOURCE_DIR):
    files = os.listdir(SOURCE_DIR)
    if files:
        st.markdown("### 📄 目前資料夾內檔案：")
        for file in files:
            st.write(f"• {file}")
    else:
        st.info("目前尚未上傳任何文件。")
else:
    os.makedirs(SOURCE_DIR)
    st.info("已自動建立 source_documents 資料夾，請放入你的文件。")
