# private_gpt.py
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
import os
import openai

load_dotenv()

def load_llm():
    return ChatOpenAI(temperature=0, model_name="gpt-4o")

def get_answer(query, llm):
    embeddings = OpenAIEmbeddings()
    db = FAISS.load_local("vectorstore", embeddings, allow_dangerous_deserialization=True)
    retriever = db.as_retriever()
    qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

    try:
        result = qa(query)
        return result["result"], result.get("source_documents", [])
    except openai.error.APIConnectionError:
        return "⚠️ 無法連線，請檢查網路。", []
    except openai.error.AuthenticationError:
        return "❌ 金鑰錯誤，請重新設定。", []
    except Exception as e:
        return f"🚨 發生未知錯誤：{str(e)}", []
