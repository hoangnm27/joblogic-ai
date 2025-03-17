import streamlit as st
import requests
import time

# 🚀 Lấy API Key từ Streamlit Secrets
OPENAI_API_KEY = st.secrets["openai_api_key"]

# 🔥 Config API (Có thể đổi sang API nội bộ công ty)
BACKEND_URL = "https://api.openai.com/v1"  # Sử dụng OpenAI trực tiếp
ASSISTANT_ID_1 = "asst_O7obur1KCwjWEi43oLd6vgla"
ASSISTANT_ID_2 = "asst_cfoXdMTHow5kPmrYEtNtD2Hu"

# 📌 Hàm gọi API Backend
def call_backend_api(url, method, body=None):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "assistants=v2"
    }
    response = requests.request(method, f"{BACKEND_URL}{url}", headers=headers, json=body)
    return response.json()

# 🚀 Streamlit UI
st.title("Joblogic AI Assistant")

# 📌 Tabs (Joblogic Business Knowledge & Generate Test Cases)
tab1, tab2 = st.tabs(["Joblogic Business Knowledge", "Generate Test Cases"])

# ✅ Tab 1 - Joblogic Business Knowledge
with tab1:
    st.subheader("Input the request:")
    prompt1 = st.text_area("Prompt:", key="prompt1")
    if st.button("Ask Job Logic AI", key="btn1"):
        with st.spinner("⏳ In Progress..."):
            thread_data = call_backend_api("/threads", "POST")
            thread_id = thread_data.get("id")

            call_backend_api(f"/threads/{thread_id}/messages", "POST", {"role": "user", "content": prompt1})
            run_data = call_backend_api(f"/threads/{thread_id}/runs", "POST", {"assistant_id": ASSISTANT_ID_1})
            run_id = run_data.get("id")

            status = ""
            while status != "completed":
                time.sleep(5)
                status_data = call_backend_api(f"/threads/{thread_id}/runs/{run_id}", "GET")
                status = status_data.get("status", "")

            messages_data = call_backend_api(f"/threads/{thread_id}/messages", "GET")
            correct_message = next((msg for msg in messages_data["data"] if msg["run_id"] == run_id), None)

            if correct_message:
                extracted_text = "\n".join(item["text"]["value"] for item in correct_message["content"])
                st.success("✅ Enjoy:")
                st.write(extracted_text)
            else:
                st.error("❌ No response data!")

# ✅ Tab 2 - Generate Test Cases
with tab2:
    st.subheader("Input the request:")
    prompt2 = st.text_area("Prompt:", key="prompt2")
    if st.button("Generate Test Cases", key="btn2"):
        with st.spinner("⏳ In Progress..."):
            thread_data = call_backend_api("/threads", "POST")
            thread_id = thread_data.get("id")

            call_backend_api(f"/threads/{thread_id}/messages", "POST", {"role": "user", "content": prompt2})
            run_data = call_backend_api(f"/threads/{thread_id}/runs", "POST", {"assistant_id": ASSISTANT_ID_2})
            run_id = run_data.get("id")

            status = ""
            while status != "completed":
                time.sleep(5)
                status_data = call_backend_api(f"/threads/{thread_id}/runs/{run_id}", "GET")
                status = status_data.get("status", "")

            messages_data = call_backend_api(f"/threads/{thread_id}/messages", "GET")
            correct_message = next((msg for msg in messages_data["data"] if msg["run_id"] == run_id), None)

            if correct_message:
                extracted_text = "\n".join(item["text"]["value"] for item in correct_message["content"])
                st.success("✅ Test Cases:")
                st.write(extracted_text)
            else:
                st.error("❌ No Test Cases available!")
