# private_gpt.py
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
import os
import openai
from openai import OpenAIError
from openai._exceptions import APIConnectionError, AuthenticationError

load_dotenv()

def load_llm():
    return ChatOpenAI(temperature=0, model_name="gpt-4o")

def clean_source_path(source_path):
    """去除路徑前綴，只返回文件名"""
    return os.path.basename(source_path)

def get_answer(query, llm):
    embeddings = OpenAIEmbeddings()
    db = FAISS.load_local("vectorstore", embeddings, allow_dangerous_deserialization=True)
    retriever = db.as_retriever(search_kwargs={"k": 3})  # 限制返回結果數量
    
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )

    try:
        result = qa({"query": query})
        # 去重處理
        unique_sources = set()
        cleaned_docs = []
        for doc in result["source_documents"]:
            if hasattr(doc, 'metadata'):
                # 徹底清理路徑
                doc.metadata['source'] = os.path.basename(doc.metadata.get('source', ''))
                if doc.metadata['source'] not in unique_sources:
                    unique_sources.add(doc.metadata['source'])
                    cleaned_docs.append(doc)
        
        return result["result"], cleaned_docs
    except APIConnectionError:
        return "⚠️ 無法連線至 OpenAI API", []
    except AuthenticationError:
        return "❌ OpenAI API 金鑰錯誤", []
    except OpenAIError as e:
        return f"🚨 OpenAI 錯誤：{e}", []
