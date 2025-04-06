# ingest.py（已更新支援 OCR PDF、加入筆數提示）
import os
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

# 在 ingest.py 的 load_single_document 函數中添加
def load_single_document(filepath):
    if filepath.endswith(".pdf"):
        loader = PyMuPDFLoader(filepath)
    elif filepath.endswith(".txt"):
        loader = TextLoader(filepath)
    elif filepath.endswith(".docx"):
        loader = Docx2txtLoader(filepath)
    else:
        raise ValueError("Unsupported file type")
    
    docs = loader.load()
    # 清理metadata中的路徑
    for doc in docs:
        if 'source' in doc.metadata:
            doc.metadata['source'] = os.path.basename(doc.metadata['source'])
    return docs

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

def ingest_all():
    print("📄 掃描資料夾：source_documents")
    source_dir = "source_documents"
    documents = []
    for filename in os.listdir(source_dir):
        filepath = os.path.join(source_dir, filename)
        if filename.endswith((".pdf", ".txt", ".docx")):
            documents.extend(load_single_document(filepath))
    if not documents:
        print("⚠️ 未找到任何可處理文件。")
        return
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)
    embeddings = OpenAIEmbeddings()
    db = FAISS.from_documents(texts, embeddings)
    db.save_local("vectorstore")
    print(f"✅ 向量化完成，共處理段落數：{len(texts)}")

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
