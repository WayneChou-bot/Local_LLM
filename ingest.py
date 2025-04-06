import os
from langchain.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

def load_documents(source_dir):
    documents = []
    for filename in os.listdir(source_dir):
        filepath = os.path.join(source_dir, filename)
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(filepath)
        elif filename.endswith(".txt"):
            loader = TextLoader(filepath)
        elif filename.endswith(".docx"):
            loader = Docx2txtLoader(filepath)
        else:
            print(f"❌ Unsupported file format: {filename}")
            continue
        docs = loader.load()
        documents.extend(docs)
    return documents

def ingest():
    print("📄 Loading documents...")
    documents = load_documents("source_documents")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(documents)

    print("🔍 Creating embeddings and saving to FAISS...")
    embeddings = OpenAIEmbeddings()
    db = FAISS.from_documents(texts, embeddings)
    db.save_local("vectorstore")
    print("✅ Ingestion complete.")

if __name__ == "__main__":
    ingest()
