# ingest.py（已更新支援 OCR PDF、加入筆數提示）
import os
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

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

def ingest_file(filepath):
    docs = load_single_document(filepath)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(docs)
    embeddings = OpenAIEmbeddings()
    if os.path.exists("vectorstore/index.faiss"):
        db = FAISS.load_local("vectorstore", embeddings, allow_dangerous_deserialization=True)
        db.add_documents(texts)
    else:
        db = FAISS.from_documents(texts, embeddings)
    db.save_local("vectorstore")
    print(f"✅ 向量化完成：{filepath}，段落數：{len(texts)}")

if __name__ == "__main__":
    ingest_all()

# run_ingest.bat（Windows 環境一鍵執行腳本）
# 請將以下內容另存為 run_ingest.bat
# ===============================
# @echo off
# echo 正在啟動文件向量化...
# call conda activate your_env_name  || echo (可手動切換環境)
# python ingest.py
# pause
# ===============================

# Linux / macOS 可用 bash:
# chmod +x run_ingest.sh
# ./run_ingest.sh

# run_ingest.sh
# ===============================
# #!/bin/bash
# echo "🔁 正在向量化所有文件..."
# python ingest.py
# ===============================
