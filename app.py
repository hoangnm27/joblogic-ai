import streamlit as st
import requests
import time

# 🚀 Cấu hình UI
st.set_page_config(
    page_title="Joblogic AI",  # Hiển thị tên trên tab browser
    page_icon="Icon-60x60.png",  # Biểu tượng favicon
    layout="wide"
)

# 🚀 Load API key từ Streamlit secrets
OPENAI_API_KEY = st.secrets["openai_api_key"]

# 🔥 Cấu hình API
BACKEND_URL = "https://api.openai.com/v1"
ASSISTANT_ID = "asst_cfoXdMTHow5kPmrYEtNtD2Hu"  # Chỉ giữ lại Generate Test Cases

# ✅ Khởi tạo session state nếu chưa có
if "chat_history" not in st.session_state or not isinstance(st.session_state["chat_history"], list):
    st.session_state["chat_history"] = []
if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = None

# 📌 Gọi API OpenAI
def call_openai_api(thread_id, message):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "assistants=v2"
    }

    # Gửi tin nhắn vào thread
    msg_res = requests.post(
        f"{BACKEND_URL}/threads/{thread_id}/messages",
        headers=headers,
        json={"role": "user", "content": message}
    )

    if msg_res.status_code != 200:
        return "❌ Error sending message!"

    # Chạy Assistant để lấy phản hồi
    run_res = requests.post(
        f"{BACKEND_URL}/threads/{thread_id}/runs",
        headers=headers,
        json={"assistant_id": ASSISTANT_ID}
    )

    if run_res.status_code != 200:
        return "❌ Error starting assistant run!"

    run_id = run_res.json().get("id")

    # ⏳ Loading AI trả lời
    with st.spinner("⏳ AI is reviewing..."):
        status = ""
        while status != "completed":
            time.sleep(5)
            status_res = requests.get(
                f"{BACKEND_URL}/threads/{thread_id}/runs/{run_id}",
                headers=headers
            )
            status = status_res.json().get("status")

    # Lấy dữ liệu phản hồi
    messages_res = requests.get(
        f"{BACKEND_URL}/threads/{thread_id}/messages",
        headers=headers
    )

    if messages_res.status_code != 200:
        return "❌ Error retrieving response!"

    messages = messages_res.json()["data"]
    response = next((msg for msg in messages if msg["run_id"] == run_id), None)

    return response["content"][0]["text"]["value"] if response else "❌ No response!"

# ✅ Kiểm tra thread_id
if st.session_state["thread_id"] is None:
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
        st.error(f"❌ Error creating thread: {thread_json}")
        st.stop()

thread_id = st.session_state["thread_id"]

# 📌 Giao diện chính
st.title("💬 Generate Test Cases Chatbot")

# ✅ Hiển thị lịch sử chat
for msg in st.session_state["chat_history"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ✅ Ô nhập tin nhắn
user_input = st.chat_input("Input your message...")

# ✅ Xử lý gửi tin nhắn
if user_input:
    # 👉 Thêm tin nhắn người dùng vào lịch sử
    st.session_state["chat_history"].append({"role": "user", "content": user_input})

    # ✅ Hiển thị tin nhắn của người dùng
    with st.chat_message("user"):
        st.write(user_input)

    # ✅ Gửi tin nhắn đến Assistant
    response = call_openai_api(thread_id, user_input)

    # ✅ Thêm tin nhắn AI vào lịch sử
    st.session_state["chat_history"].append({"role": "assistant", "content": response})

    # ✅ Hiển thị tin nhắn AI
    with st.chat_message("assistant"):
        st.write(response)

    # ✅ Cập nhật trang
    st.rerun()
