# ✅ app.py: Supports dark UI, automatic vectorization, stable Q&A, and "clear input box after submission" - Fixed TypeError

import streamlit as st
import os
import time  # Used to simulate processing delay (if needed)
from PIL import Image  # If you need to display a logo
from ingest import ingest_file

# Check if the vector database already exists; if not, run ingest
if not os.path.exists("vectorstore/index.faiss"):
    with st.spinner("Building the knowledge base, please wait... (this may take some time)"):
        ingest_file()
    st.success("Knowledge base has been successfully created!")

# --- Module imports (Adjust according to your project structure) ---
# Ensure these import paths and function names match your 'private_gpt' and 'ingest' modules
try:
    from private_gpt import load_llm, get_answer
    from ingest import ingest_file
except ImportError as e:
    st.error(f"Failed to import required modules (private_gpt, ingest): {e}")
    st.info("Please make sure 'private_gpt.py' and 'ingest.py' exist in the project directory or Python path, and include the required 'load_llm', 'get_answer', 'ingest_file' functions.")
    st.stop()  # Stop the app if core functionalities can't be loaded

# --- Page configuration ---
st.set_page_config(
    page_title="Enterprise Q&A System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for dark mode theme ---
st.markdown("""
    <style>
        body {
            background-color: #0F172A; /* Dark navy background */
            color: #F1F5F9; /* Light gray text */
        }
        .main-title {
            font-size: 34px;
            font-weight: 900;
            color: #60A5FA; /* Light blue */
            margin-bottom: 0;
            padding-top: 0.5rem;
        }
        .sub-title {
            font-size: 16px;
            color: #94A3B8; /* Gray-blue */
            margin-top: 0;
            margin-bottom: 1rem;
        }
        .response-box {
            background-color: #1E293B; /* Dark blue-gray */
            color: #F8FAFC; /* Near white */
            padding: 1.5rem;
            border-radius: 10px;
            font-size: 16px;
            border: 1px solid #334155;
            margin-top: 1rem;
        }
        .stSidebar > div:first-child {
            background-color: #1E293B;
            color: #F8FAFC;
        }
        .uploaded-file {
            background-color: #334155; /* Lighter blue-gray */
            color: #E0F2FE; /* Light sky blue */
            padding: 6px 10px;
            border-radius: 8px;
            margin: 4px 0;
            font-size: 14px;
            display: flex;
            align-items: center;
        }
        .uploaded-file-icon {
            margin-right: 8px;
        }
        .stTextInput label, .stFileUploader label {
            color: #CBD5E1;
            font-weight: 600;
        }
        .stTextInput input {
            background-color: #0F172A;
            color: #F1F5F9;
            border: 1px solid #334155;
        }
        .stButton>button {
            background-color: #2563EB;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-weight: 600;
            width: 100%;
            margin-top: 0.5rem;
        }
        .stButton>button:hover {
            background-color: #1D4ED8;
            color: white;
        }
        hr {
            border-top: 1px solid #334155;
        }
    </style>
""", unsafe_allow_html=True)

# --- Initialize session state ---
if "query_input_value" not in st.session_state:
    st.session_state.query_input_value = ""
if "query_to_process" not in st.session_state:
    st.session_state.query_to_process = ""
# if "chat_history" not in st.session_state: # Optional: chat history tracking
#     st.session_state.chat_history = []

# --- Callback function ---
def submit_query():
    """Triggered when the user clicks the submit button"""
    st.session_state.query_to_process = st.session_state.query_input_value
    st.session_state.query_input_value = ""

# --- Sidebar ---
with st.sidebar:
    # st.image("path/to/your/logo.png", width=100) # Optionally display a logo here
    st.markdown("<div class='main-title'>🧠 Smart Q&A Assistant</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>AI-powered Q&A based on internal documents</div>", unsafe_allow_html=True)
    st.markdown("---")

    st.subheader("💬 Ask a Question")
    st.text_input(
        "Enter your question:",
        key="query_input_value",
        value=st.session_state.query_input_value,
        placeholder="e.g., What is our product warranty period?",
        label_visibility="collapsed"
    )
    st.button("Submit Question", on_click=submit_query)

    st.markdown("---")

    st.subheader("📁 Document Management")
    uploaded_files = st.file_uploader(
        "Upload new documents (PDF/TXT/DOCX):",
        type=["pdf", "txt", "docx"],  # Adjust based on your ingest.py support
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    # File handling logic
    source_dir = "source_documents"  # Assuming your vectorized data comes from this folder
    if not os.path.exists(source_dir):
        try:
            os.makedirs(source_dir)
        except OSError as e:
            st.error(f"Failed to create source_documents directory: {e}")
            st.stop()  # Stop the app if the required folder can't be created

    if uploaded_files:
        progress_bar = st.progress(0, text="Preparing to process files...")
        total_files = len(uploaded_files)
        files_processed = 0
        for i, uploaded_file in enumerate(uploaded_files):
            filename = uploaded_file.name
            filepath = os.path.join(source_dir, filename)
            progress_text = f"Processing: {filename} ({i+1}/{total_files})"
            progress_bar.progress((i + 1) / total_files, text=progress_text)

            try:
                # Save file to source_documents
                with open(filepath, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.write(f"File '{filename}' has been saved. Starting vectorization...")

                # Vectorize the file (ensure ingest_file exists and supports single file processing)
                ingest_file(filepath)
                files_processed += 1
                st.write(f"'{filename}' vectorization completed.")

            except Exception as e:
                st.error(f"Error processing file '{filename}': {e}")
                # Optionally delete files that failed to process
                # if os.path.exists(filepath):
                #     os.remove(filepath)

        progress_bar.empty()
        if files_processed > 0:
            st.success(f"✅ {files_processed} new files have been successfully uploaded and vectorized.")
            # Optionally reload LLM or vector store if needed
            # st.cache_resource.clear()
        else:
            st.warning("Files were uploaded, but none were processed successfully.")

    st.markdown("### 📚 Current Knowledge Base Files:")
    if os.path.exists(source_dir) and os.path.isdir(source_dir):
        try:
            files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f))]
            if files:
                for f in files:
                    st.markdown(f"<div class='uploaded-file'><span class='uploaded-file-icon'>📄</span>{f}</div>", unsafe_allow_html=True)
            else:
                st.info("There are currently no documents in the knowledge base.")
        except Exception as e:
            st.error(f"Error reading file list: {e}")
    else:
        st.info(f"Source folder '{source_dir}' does not exist. Please upload files to begin.")

# --- Main Area ---
st.markdown("<div class='main-title'>📣 Answer Result</div>", unsafe_allow_html=True)

# --- Cache LLM loading ---
@st.cache_resource
def cached_load_llm():
    """Cache LLM loading to improve performance"""
    loading_message = st.info("Loading the LLM model for the first time... (this may take a moment)")
    try:
        llm = load_llm()
        loading_message.success("LLM model loaded successfully!")
        return llm
    except Exception as e:
        loading_message.error(f"Error loading LLM model: {e}")
        st.exception(e)
        return None

# Load the cached LLM
llm = cached_load_llm()

# --- Q&A logic ---
if st.session_state.query_to_process:
    current_query = st.session_state.query_to_process

    if llm:
        with st.spinner("⏳ AI is thinking, please wait..."):
            try:
                response, sources = get_answer(current_query, llm)

                st.markdown(f"<div class='response-box'>{response}</div>", unsafe_allow_html=True)

                if sources:
                    st.subheader("📄 Reference Sources")
                    source_list = []
                    if isinstance(sources, list):
                        for doc in sources:
                            if hasattr(doc, 'metadata') and isinstance(doc.metadata, dict):
                                source_path = doc.metadata.get("source", "Unknown source")
                                source_name = os.path.basename(str(source_path)).strip().replace("\\", "/").split("/")[-1]
                                if source_name not in source_list:
                                    source_list.append(source_name)
                            else:
                                st.warning("Detected unexpected document structure. Some references may not be shown.")
                        if source_list:
                            for name in source_list:
                                clean_name = os.path.basename(name)
                                st.markdown(f"- **{clean_name}**")
                        else:
                            st.info("ℹ️ The answer was generated, but no clear reference source name could be extracted.")
                    else:
                        st.info("ℹ️ The answer was generated, but the source format was not a list.")
                else:
                    st.info("ℹ️ No relevant reference sources found in the knowledge base.")
            except Exception as e:
                st.error(f"An error occurred while processing the query '{current_query}':")
                st.exception(e)
    else:
        st.error("LLM model failed to load. Unable to process the query. Please check logs or settings.")

    st.session_state.query_to_process = ""

elif not llm:
    st.error("Critical LLM model failed to load. The application cannot operate. Please check your environment and configuration.")

else:
    st.markdown("<div class='response-box' style='text-align: center; padding: 2rem;'>Please enter your question in the left panel and click the 'Submit Question' button.</div>", unsafe_allow_html=True)

# --- Footer (optional) ---
st.markdown("---")
st.caption(f"© {time.strftime('%Y')} [StockSeek] - Internal AI Q&A System | {st.__version__}")
