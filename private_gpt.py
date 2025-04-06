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
    return ChatOpenAI(temperature=0.7, model_name="gpt-4o-mini")

def get_answer(query, llm):
    embeddings = OpenAIEmbeddings()
    db = FAISS.load_local("vectorstore", embeddings, allow_dangerous_deserialization=True)
    retriever = db.as_retriever()
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )
    result = qa({"query": query})
    return result['result'], result.get("source_documents", [])

    try:
        result = qa(query)
        return result["result"], result.get("source_documents", [])
    except APIConnectionError:
        return "⚠️ 無法連線", []
    except AuthenticationError:
        return "❌ 金鑰錯誤", []
    except OpenAIError as e:
        return f"🚨 LLM 錯誤：{e}", []
