# ✅ app.py：支援深色 UI、自動向量化、穩定問答與「提交後清空輸入框」 - 修正 TypeError
import streamlit as st
import os
import time # 用於模擬處理延遲 (如果需要)
from PIL import Image # 如果需要顯示 Logo
from ingest import ingest_file

# 檢查向量資料夾是否已存在，如果不存在就執行 ingest
if not os.path.exists("vectorstore/index.faiss"):
    ingest_file()

# --- 假設的導入 (請根據你的專案結構確認) ---
# 確保這些導入路徑和函數名稱與你的 'private_gpt' 和 'ingest' 模組一致
try:
    from private_gpt import load_llm, get_answer
    from ingest import ingest_file
except ImportError as e:
    st.error(f"無法導入必要的模組 (private_gpt, ingest): {e}")
    st.info("請確保 'private_gpt.py' 和 'ingest.py' 文件存在於專案目錄或 Python 路徑中，並且包含所需的 'load_llm', 'get_answer', 'ingest_file' 函數。")
    st.stop() # 如果無法導入核心功能，停止應用程式

# --- 頁面基礎設定 ---
st.set_page_config(
    page_title="企業智慧問答系統",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS 深色主題設計 ---
st.markdown("""
    <style>
        body {
            background-color: #0F172A; /* 深藍灰背景 */
            color: #F1F5F9; /* 亮灰色文字 */
        }
        /* 主標題 */
        .main-title {
            font-size: 34px;
            font-weight: 900;
            color: #60A5FA; /* 淺藍色 */
            margin-bottom: 0;
            padding-top: 0.5rem;
        }
        /* 副標題 */
        .sub-title {
            font-size: 16px;
            color: #94A3B8; /* 灰藍色 */
            margin-top: 0;
            margin-bottom: 1rem;
        }
        /* 回應框 */
        .response-box {
            background-color: #1E293B; /* 深藍灰 */
            color: #F8FAFC; /* 近白色 */
            padding: 1.5rem;
            border-radius: 10px;
            font-size: 16px;
            border: 1px solid #334155; /* 添加細邊框 */
            margin-top: 1rem;
        }
        /* 側邊欄 */
        .stSidebar > div:first-child {
            background-color: #1E293B;
            color: #F8FAFC;
        }
        /* 上傳的文件標示 */
        .uploaded-file {
            background-color: #334155; /* 較淺藍灰 */
            color: #E0F2FE; /* 淺天藍 */
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
        /* 輸入框和標籤 */
        .stTextInput label, .stFileUploader label {
            color: #CBD5E1;
            font-weight: 600;
        }
        .stTextInput input {
            background-color: #0F172A;
            color: #F1F5F9;
            border: 1px solid #334155;
        }
        /* 按鈕樣式 */
        .stButton>button {
            background-color: #2563EB; /* 主題藍色 */
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
        /* 分隔線 */
        hr {
            border-top: 1px solid #334155;
        }
    </style>
""", unsafe_allow_html=True)

# --- 狀態初始化 ---
if "query_input_value" not in st.session_state:
    st.session_state.query_input_value = ""
if "query_to_process" not in st.session_state:
    st.session_state.query_to_process = ""
# if "chat_history" not in st.session_state: # 可選：聊天歷史記錄
#     st.session_state.chat_history = []

# --- 回調函數 ---
def submit_query():
    """當用戶點擊提交按鈕時觸發"""
    st.session_state.query_to_process = st.session_state.query_input_value
    st.session_state.query_input_value = ""

# --- 側邊欄 (Sidebar) ---
with st.sidebar:
    # st.image("path/to/your/logo.png", width=100) # 可在此處放置 Logo
    st.markdown("<div class='main-title'>🧠 智慧問答助手</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>基於內部文件的 AI 問答</div>", unsafe_allow_html=True)
    st.markdown("---")

    st.subheader("💬 問題提問")
    st.text_input(
        "請輸入你的問題：",
        key="query_input_value",
        value=st.session_state.query_input_value,
        placeholder="例如：我們的產品保固期多久？",
        label_visibility="collapsed"
    )
    st.button("提交問題", on_click=submit_query)

    st.markdown("---")

    st.subheader("📁 文件管理")
    uploaded_files = st.file_uploader(
        "上傳新文件 (PDF/TXT/DOCX):",
        type=["pdf", "txt", "docx"], # 根據你的 ingest.py 支援調整
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    # 文件處理邏輯
    source_dir = "source_documents" # 假設你的向量化資料來源於此
    if not os.path.exists(source_dir):
        try:
            os.makedirs(source_dir)
        except OSError as e:
            st.error(f"無法建立資料來源資料夾 '{source_dir}': {e}")
            st.stop() # 如果無法建立必要資料夾，停止

    if uploaded_files:
        progress_bar = st.progress(0, text="準備開始處理文件...")
        total_files = len(uploaded_files)
        files_processed = 0
        for i, uploaded_file in enumerate(uploaded_files):
            filename = uploaded_file.name
            filepath = os.path.join(source_dir, filename)
            progress_text = f"處理中：{filename} ({i+1}/{total_files})"
            progress_bar.progress((i + 1) / total_files, text=progress_text)

            try:
                # 寫入文件到 source_documents
                with open(filepath, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.write(f"文件 '{filename}' 已儲存，開始向量化...")

                # 調用向量化函數 (確保 ingest_file 存在且能處理單一文件)
                ingest_file(filepath) # 假設此函數處理向量化
                files_processed += 1
                st.write(f"'{filename}' 向量化完成。")

            except Exception as e:
                 st.error(f"處理文件 '{filename}' 時發生錯誤: {e}")
                 # 可考慮是否刪除儲存失敗或處理失敗的文件
                 # if os.path.exists(filepath):
                 #     os.remove(filepath)

        progress_bar.empty() # 完成後清除進度條
        if files_processed > 0:
            st.success(f"✅ {files_processed} 個新文件已成功上傳並向量化。")
            # 可考慮觸發一次 LLM 或向量庫的重新載入（如果需要）
            # st.cache_resource.clear() # 如果 LLM 或向量庫需要感知新文件
        else:
            st.warning("文件上傳完成，但未能成功處理任何文件。")


    st.markdown("### 📚 現有知識庫文件：")
    if os.path.exists(source_dir) and os.path.isdir(source_dir):
        try:
            files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f))]
            if files:
                for f in files:
                    st.markdown(f"<div class='uploaded-file'><span class='uploaded-file-icon'>📄</span>{f}</div>", unsafe_allow_html=True)
            else:
                st.info("知識庫中目前沒有文件。")
        except Exception as e:
            st.error(f"讀取文件列表時出錯: {e}")
    else:
        st.info(f"資料來源資料夾 '{source_dir}' 不存在。請上傳文件以開始。")


# --- 主畫面 (Main Area) ---
st.markdown("<div class='main-title'>📣 問答結果</div>", unsafe_allow_html=True)

# --- 快取 LLM 模型載入 ---
@st.cache_resource
def cached_load_llm():
    """快取載入 LLM 模型以提高效能"""
    loading_message = st.info("首次載入 LLM 模型... (可能需要一點時間)")
    try:
        llm = load_llm() # 從 private_gpt 模組載入模型
        loading_message.success("LLM 模型載入成功！")
        return llm
    except Exception as e:
        loading_message.error(f"載入 LLM 模型時發生錯誤: {e}")
        st.exception(e) # 顯示詳細錯誤給開發者
        return None # 載入失敗返回 None

# 載入快取的 LLM 模型
llm = cached_load_llm()

# --- 問答處理邏輯 ---
# 檢查是否有待處理的問題
if st.session_state.query_to_process:
    current_query = st.session_state.query_to_process

    # 確保 LLM 已成功載入
    if llm:
        # 執行問答
        with st.spinner("⏳ AI 正在思考中，請稍候..."):
            try:
                # 執行查詢，傳入 llm 參數
                response, sources = get_answer(current_query, llm)

                # 顯示回答
                st.markdown(f"<div class='response-box'>{response}</div>", unsafe_allow_html=True)

                # 顯示來源
                if sources:
                    st.subheader("📄 參考來源")
                    
                    # 檢查 sources 是否可迭代且包含有效的 doc 物件
                    if isinstance(sources, list):
                         for doc in sources:
                             # 檢查 doc 是否有 metadata 屬性且 metadata 是字典
                             if hasattr(doc, 'metadata') and isinstance(doc.metadata, dict):
                                 source_path = doc.metadata.get("source", "未知來源")
                                 source_name = os.path.basename(source_path) # 只取文件名
                                 if source_name not in source_list:
                                     source_list.append(source_name)
                             else:
                                 # 如果 doc 結構不符合預期，可以記錄或跳過
                                 st.warning("偵測到來源文件結構異常，部分來源可能無法顯示。")

                         if source_list:
                             for name in source_list:
                                 clean_name = os.path.basename(name)  # 再次確保只取檔名
                                 st.markdown(f"- **{clean_name}**")  # 更清楚且美觀
                         else:
                             st.info("ℹ️ 回答已生成，但未能從知識庫文件中解析出明確的參考來源檔名。")
                    else:
                         st.info("ℹ️ 回答已生成，但來源資訊格式非預期列表。")
                else:
                    st.info("ℹ️ 未能從知識庫文件中找到直接相關的參考來源。")

            except Exception as e:
                st.error(f"處理問題 '{current_query}' 時發生錯誤：")
                st.exception(e) # 顯示詳細錯誤堆疊
    else:
        # 如果 LLM 未能載入，顯示錯誤訊息
        st.error("LLM 模型未能成功載入，無法處理查詢。請檢查日誌或設定。")

    # 處理完畢後，清除待處理標記
    st.session_state.query_to_process = ""

elif not llm:
     # 如果 LLM 在初始載入時就失敗了，在主畫面提示
     st.error("關鍵的 LLM 模型未能載入，應用程式無法正常運作。請檢查設定與環境。")

else:
    # 如果沒有待處理的問題，且 LLM 正常，顯示提示信息
    st.markdown("<div class='response-box' style='text-align: center; padding: 2rem;'>請在左側輸入您的問題，然後點擊「提交問題」按鈕。</div>", unsafe_allow_html=True)


# --- (可選) 添加頁腳 ---
st.markdown("---")
st.caption(f"© {time.strftime('%Y')} [StockSeek] - 內部 AI 智慧問答系統 | {st.__version__}") # 使用當前年份和 Streamlit 版本
