# 🧠 智慧問答系統（RAG + ChatGPT + Streamlit）

這是一個結合 RAG 架構與 ChatGPT 的企業內部文件問答系統，使用者可於網頁介面輸入問題，即可查詢 PDF/TXT/DOCX 文件並獲得智慧回答。

## ✨ 系統特色
- GPT-4o 模型回答
- 向量檢索結合 LangChain + FAISS
- 文件資料來源顯示
- 直觀 Streamlit UI

## 🚀 快速開始

```bash
git clone https://github.com/your-username/privategpt-enterprise-ui.git
cd privategpt-enterprise-ui

# 安裝套件
pip install -r requirements.txt

# 放入你的文件到 source_documents/
python ingest.py

# 啟動 UI
streamlit run app.py
```

## ☁️ 部署到 Streamlit Cloud

在 Streamlit Cloud 專案設定 secrets：

```
OPENAI_API_KEY=your-key
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL_NAME=text-embedding-3-small
LLM_PROVIDER=openai
MODEL_NAME=gpt-4o-mini
```

## 📁 專案結構

```
├── app.py
├── private_gpt.py
├── ingest.py
├── requirements.txt
├── .env.example
├── source_documents/
├── vectorstore/  (執行 ingest 後自動產生)
```

## 🙌 作者
- Wayne Chou

### 📚 致謝
本專案靈感源自 [privateGPT](https://github.com/imartinez/privateGPT)，並基於其架構重構成簡潔的企業級版本。
