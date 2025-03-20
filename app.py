import streamlit as st
import requests
import time

# 🚀 Config UI
st.set_page_config(
    page_title="Joblogic Chatbot",  # Browser Title
    page_icon="Icon-60x60.png",  # icon
    layout="wide"
)

# 🚀 Load API key from the streamlit secret
OPENAI_API_KEY = st.secrets["openai_api_key"]

# 🔥 Call API
BACKEND_URL = "https://api.openai.com/v1"
ASSISTANT_ID = "asst_cfoXdMTHow5kPmrYEtNtD2Hu"

# ✅ Initialize session state if not have
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = None


# 📌 Call function OpenAI API
def call_openai_api(thread_id, message):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "assistants=v2"
    }

    # Send message to the thread
    requests.post(
        f"{BACKEND_URL}/threads/{thread_id}/messages",
        headers=headers,
        json={"role": "user", "content": message}
    )

    # Run Assistant to get response
    run_res = requests.post(
        f"{BACKEND_URL}/threads/{thread_id}/runs",
        headers=headers,
        json={"assistant_id": ASSISTANT_ID}
    )
    run_id = run_res.json().get("id")

    # ⏳ Show loading
    with st.spinner("⏳ AI is reviewing..."):
        status = ""
        while status != "completed":
            time.sleep(5)
            status_res = requests.get(
                f"{BACKEND_URL}/threads/{thread_id}/runs/{run_id}",
                headers=headers
            )
            status = status_res.json().get("status")

    # Get the response data
    messages_res = requests.get(
        f"{BACKEND_URL}/threads/{thread_id}/messages",
        headers=headers
    )
    messages = messages_res.json()["data"]
    response = next((msg for msg in messages if msg["run_id"] == run_id), None)

    return response["content"][0]["text"]["value"] if response else "❌ No response!"

# 🎨 Custom CSS for UI
st.markdown(
    """
    <style>
        .block-container {
            max-width: 85%;
            margin-left: auto;
            margin-right: auto;
        }
        .sidebar .sidebar-content {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# 🚀 Sidebar - Joblogic logo
logo_path = "Medium square transparent logo_300x178.png" 
st.sidebar.image(logo_path, use_container_width=True)

# ✅ Check thread_id
if not st.session_state["thread_id"]:
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "assistants=v2"
    }
    thread_res = requests.post(f"{BACKEND_URL}/threads", headers=headers)
    thread_json = thread_res.json()
    if "id" in thread_json:
        st.session_state["thread_id"] = thread_json["id"]
    else:
        st.error(f"❌ Error of creating thread: {thread_json}")
        st.stop()

thread_id = st.session_state["thread_id"]

# 🚀 Chatbot Title
st.title("💬 Generate Test Cases Chatbot")

# ✅ Show conversation history
for msg in st.session_state["chat_history"]:
    if isinstance(msg, dict) and "role" in msg and "content" in msg:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])



# ✅ Message box
user_input = st.chat_input("Input your message...")

# ✅ Loading
if st.session_state.get("loading", False):
    with st.spinner("⏳ AI is reviewing..."):
        time.sleep(1)

# ✅ Send message
if user_input:
    # 👉 Thêm tin nhắn của user vào lịch sử trước khi gọi API
    st.session_state["chat_history"].append({"role": "user", "content": user_input})

    # ✅ Hiển thị tin nhắn của user
    with st.chat_message("user"):
        st.write(user_input)

    # ✅ Gửi message đến API và nhận phản hồi
    response = call_openai_api(st.session_state["thread_id"], user_input, assistant_id)

    # 👉 Thêm phản hồi của AI vào lịch sử
    st.session_state["chat_history"].append({"role": "assistant", "content": response})

    # ✅ Hiển thị tin nhắn của AI
    with st.chat_message("assistant"):
        st.write(response)

