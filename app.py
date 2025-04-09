# ✅ app.py: Supports Dark UI, Automatic Vectorization, Stable Q&A, and "Clear Input Box After Submission" - Fixed TypeError

import streamlit as st
import os
import time  # Used to simulate processing delays (if needed)
from PIL import Image  # If needed to display a Logo
from ingest import ingest_file

# Check if the vector folder exists; if not, run ingest
if not os.path.exists("vectorstore/index.faiss"):
    with st.spinner("Creating knowledge base, please wait... (This may take some time)"):
        ingest_file()
    st.success("Knowledge base creation complete!")

# --- Assumed imports (please confirm based on your project structure) ---
# Ensure these import paths and function names are consistent with your 'private_gpt' and 'ingest' modules
try:
    from private_gpt import load_llm, get_answer
    from ingest import ingest_file
except ImportError as e:
    st.error(f"Unable to import required modules (private_gpt, ingest): {e}")
    st.info("Please ensure 'private_gpt.py' and 'ingest.py' files exist in the project directory or Python path and include the necessary 'load_llm', 'get_answer', 'ingest_file' functions.")
    st.stop()  # Stop the application if core functionality cannot be imported

# --- Page Basic Settings ---
st.set_page_config(
    page_title="Enterprise Intelligent Q&A System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Dark Theme Design ---
st.markdown("""
    <style>
        body {
            background-color: #0F172A; /* Dark blue-gray background */
            color: #F1F5F9; /* Light gray text */
        }
        /* Main Title */
        .main-title {
            font-size: 34px;
            font-weight: 900;
            color: #60A5FA; /* Light blue */
            margin-bottom: 0;
            padding-top: 0.5rem;
        }
        /* Subtitle */
        .sub-title {
            font-size: 16px;
            color: #94A3B8; /* Gray-blue */
            margin-top: 0;
            margin-bottom: 1rem;
        }
        /* Response Box */
        .response-box {
            background-color: #1E293B; /* Dark blue-gray */
            color: #F8FAFC; /* Near white */
            padding: 1.5rem;
            border-radius: 10px;
            font-size: 16px;
            border: 1px solid #334155; /* Add thin border */
            margin-top: 1rem;
        }
        /* Sidebar */
        .stSidebar > div:first-child {
            background-color: #1E293B;
            color: #F8FAFC;
        }
        /* Uploaded File Indicator */
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
        /* Input Box and Labels */
        .stTextInput label, .stFileUploader label {
            color: #CBD5E1;
            font-weight: 600;
        }
        .stTextInput input {
            background-color: #0F172A;
            color: #F1F5F9;
            border: 1px solid #334155;
        }
        /* Button Styles */
        .stButton>button {
            background-color: #2563EB; /* Theme blue */
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
        /* Separator Line */
        hr {
            border-top: 1px solid #334155;
        }
    </style>
""", unsafe_allow_html=True)

# --- State Initialization ---
if "query_input_value" not in st.session_state:
    st.session_state.query_input_value = ""
if "query_to_process" not in st.session_state:
    st.session_state.query_to_process = ""
# if "chat_history" not in st.session_state:  # Optional: Chat history
#   st.session_state.chat_history = []

# --- Callback Function ---
def submit_query():
    """Triggered when the user clicks the submit button"""
    st.session_state.query_to_process = st.session_state.query_input_value
    st.session_state.query_input_value = ""

# --- Sidebar ---
with st.sidebar:
    # st.image("path/to/your/logo.png", width=100)  # You can place your logo here
    st.markdown("<div class='main-title'>🧠 Intelligent Q&A Assistant</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>AI-powered Q&A Based on Internal Documents</div>", unsafe_allow_html=True)
    st.markdown("---")

    st.subheader("💬 Ask a Question")
    st.text_input(
        "Enter your question:",
        key="query_input_value",
        value=st.session_state.query_input_value,
        placeholder="e.g., What is the warranty period for our product?",
        label_visibility="collapsed"
    )
    st.button("Submit Question", on_click=submit_query)

    st.markdown("---")

    st.subheader("📁 Document Management")
    uploaded_files = st.file_uploader(
        "Upload New Documents (PDF/TXT/DOCX):",
        type=["pdf", "txt", "docx"],  # Adjust based on your ingest.py support
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    # Document processing logic
    source_dir = "source_documents"  # Assume your vectorization source is here
    if not os.path.exists(source_dir):
        try:
            os.makedirs(source_dir)
        except OSError as e:
            st.error(f"Unable to create source folder '{source_dir}': {e}")
            st.stop()  # Stop if the necessary folder cannot be created

    if uploaded_files:
        progress_bar = st.progress(0, text="Preparing to process documents...")
        total_files = len(uploaded_files)
        files_processed = 0
        for i, uploaded_file in enumerate(uploaded_files):
            filename = uploaded_file.name
            filepath = os.path.join(source_dir, filename)
            progress_text = f"Processing: {filename} ({i+1}/{total_files})"
            progress_bar.progress((i + 1) / total_files, text=progress_text)

            try:
                # Write the file to source_documents
                with open(filepath, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.write(f"File '{filename}' saved, starting vectorization...")

                # Call vectorization function (ensure ingest_file exists and can handle a single file)
                ingest_file(filepath)  # Assume this function handles vectorization
                files_processed += 1
                st.write(f"'{filename}' vectorization complete.")
            except Exception as e:
                st.error(f"Error processing file '{filename}': {e}")
                # Consider deleting the saved file if it failed to save or process
                # if os.path.exists(filepath):
                #   os.remove(filepath)

        progress_bar.empty()  # Clear progress bar after completion
        if files_processed > 0:
            st.success(f"✅ {files_processed} new files successfully uploaded and vectorized.")
            # Consider triggering a reload of the LLM or vector store (if needed)
            # st.cache_resource.clear()  # If the LLM or vector store needs to be aware of new files
        else:
            st.warning("File upload complete, but no files were successfully processed.")

    st.markdown("### 📚 Existing Knowledge Base Documents:")
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
        st.info(f"Source folder '{source_dir}' does not exist. Upload a document to get started.")

# --- Main Area ---
st.markdown("<div class='main-title'>📣 Q&A Results</div>", unsafe_allow_html=True)

# --- Cached LLM Model Loading ---
@st.cache_resource
def cached_load_llm():
    """Cached loading of LLM model to improve performance"""
    loading_message = st.info("Loading LLM model for the first time... (This may take a moment)")
    try:
        llm = load_llm()  # Load model from private_gpt module
        loading_message.success("LLM model loaded successfully!")
        return llm
    except Exception as e:
        loading_message.error(f"Error loading LLM model: {e}")
        st.exception(e)  # Display detailed error to developers
        return None  # Return None if loading fails

# Load the cached LLM model
llm = cached_load_llm()

# --- Q&A Processing Logic ---
# Check if there is a question to process
if st.session_state.query_to_process:
    current_query = st.session_state.query_to_process

    # Ensure LLM has loaded successfully
    if llm:
        # Execute the Q&A
        with st.spinner("⏳ AI is thinking, please wait..."):
            try:
                # Execute the query, passing the llm parameter
                response, sources = get_answer(current_query, llm)

                # Display the answer
                st.markdown(f"<div class='response-box'>{response}</div>", unsafe_allow_html=True)

                # Display sources
                if sources:
                    st.subheader("📄 Reference Sources")
                    source_list = []
                    # Check if sources is iterable and contains valid doc objects
                    if isinstance(sources, list):
                        for doc in sources:
                            # Check if doc has a metadata attribute and metadata is a dictionary
                            if hasattr(doc, 'metadata') and isinstance(doc.metadata, dict):
                                source_path = doc.metadata.get("source", "Unknown Source")
                                source_name = os.path.basename(str(source_path)).strip().replace("\\", "/").split("/")[-1]  # Only take the filename
                                if source_name not in source_list:
                                    source_list.append(source_name)
                            else:
                                # If the doc structure does not match expectations, you can log or skip
                                st.warning("Detected abnormal source file structure, some sources may not be displayed.")

                        if source_list:
                            for name in source_list:
                                clean_name = os.path.basename(name)  # Ensure we only take the filename again
                                st.markdown(f"- **{clean_name}**")  # Clearer and more aesthetic
                        else:
                            st.info("ℹ️ Answer generated, but unable to parse clear reference source filenames from knowledge base documents.")
                    else:
                        st.info("ℹ️ Answer generated, but source information format is not the expected list.")
                else:
                    st.info("ℹ️ No directly related reference sources found in knowledge base documents.")

            except Exception as e:
                st.error(f"Error processing question '{current_query}':")
                st.exception(e)  # Display detailed error stack
    else:
        # If the LLM fails to load, display an error message
        st.error("LLM model failed to load successfully and cannot process queries. Please check the logs or settings.")

    # Clear the pending tag after processing
    st.session_state.query_to_process = ""

elif not llm:
    # If the LLM failed during initial loading, prompt in the main area
    st.error("Critical LLM model failed to load; the application cannot function normally. Please check the settings and environment.")

else:
    # If there is no question pending and the LLM is normal, display a prompt
    st.markdown("<div class='response-box' style='text-align: center; padding: 2rem;'>Please enter your question on the left and click the 'Submit Question' button.</div>", unsafe_allow_html=True)

# --- (Optional) Add Footer ---
st.markdown("---")
st.caption(f"© {time.strftime('%Y')} [StockSeek] - Internal AI Intelligent Q&A System | {st.__version__}")  # Uses the current year and Streamlit version
