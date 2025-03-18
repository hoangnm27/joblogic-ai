import streamlit as st
import requests
#import toml
import time

'''# 🚀 Load API Key from secrets.toml
with open(".streamlit/secrets.toml", "r") as f:
    secrets = toml.load(f)
OPENAI_API_KEY = secrets["openai_api_key"]'''

# 🚀 Load API key from the streamlit secret
OPENAI_API_KEY = st.secrets["openai_api_key"]

# 🔥 Call API
BACKEND_URL = "https://api.openai.com/v1"
ASSISTANTS = {
    "Business Knowledge": "asst_O7obur1KCwjWEi43oLd6vgla",
    "Generate Test Cases": "asst_cfoXdMTHow5kPmrYEtNtD2Hu",
}

# ✅ Initialize session state if not have
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = {"Business Knowledge": [], "Generate Test Cases": []}
if "thread_ids" not in st.session_state:
    st.session_state["thread_ids"] = {}

# 📌 Call function OpenAI API
def call_openai_api(thread_id, message, assistant_id):
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
        json={"assistant_id": assistant_id}
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

# 🚀 Config UI
st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
        .block-container {
            max-width: 85%;
            margin-left: auto;
            margin-right: auto;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# 🚀 Assistant side bar
st.sidebar.title("⚙️ Assistant List")
assistant_choice = st.sidebar.radio("Select Assistant:", list(ASSISTANTS.keys()))
assistant_id = ASSISTANTS[assistant_choice]

# ✅ Check thread_id of the current Assistant
if assistant_choice not in st.session_state["thread_ids"]:
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "assistants=v2"
    }
    thread_res = requests.post(f"{BACKEND_URL}/threads", headers=headers)
    thread_json = thread_res.json()
    if "id" in thread_json:
        st.session_state["thread_ids"][assistant_choice] = thread_json["id"]
    else:
        st.error(f"❌ Error of creating thread: {thread_json}")
        st.stop()

thread_id = st.session_state["thread_ids"][assistant_choice]

st.title(f"💬 {assistant_choice} Chatbot")

# ✅ Show conversation history
for msg in st.session_state["chat_history"][assistant_choice]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ✅ Message box
user_input = st.chat_input("Input your message...")

# ✅ Loading
if st.session_state.get("loading", False):
    with st.spinner("⏳ AI is reviewing..."):
        time.sleep(1)  # Giữ hiệu ứng loading một chút trước khi cập nhật tin nhắn

# ✅ Send message
if user_input:
    st.session_state["loading"] = True  # Loading

    # 👉 Chat history
    st.session_state["chat_history"][assistant_choice].append({"role": "user", "content": user_input})

    # ✅ Show user's message
    with st.chat_message("user"):
        st.write(user_input)

    # ✅ Send message to Assistant
    response = call_openai_api(thread_id, user_input, assistant_id)

    # ✅ Add AI's message to history
    st.session_state["chat_history"][assistant_choice].append({"role": "assistant", "content": response})

    # ✅ Show AI's message
    with st.chat_message("assistant"):
        st.write(response)

    # ✅ Reset page
    st.session_state["loading"] = False  # Off loading
    st.rerun()
