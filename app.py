import streamlit as st
import requests

BACKEND_URL = "http://localhost:8001"

st.set_page_config(page_title="Support Hub", layout="wide")
st.title("🎫 Enterprise AI Support Operations Hub")

# --- BONUS FEATURE: FILTER BY STATUS ---
status_choice = st.sidebar.selectbox("🎯 Filter Operations Pipeline", ["All", "open", "in_progress", "resolved"])

# Fetch filtered tickets from backend
try:
    res = requests.get(f"{BACKEND_URL}/tickets", params={"status_filter": status_choice})
    tickets = res.json() if res.status_code == 200 else []
except Exception:
    tickets = []
    st.error("Could not reach backend API cluster service.")

# --- BONUS FEATURE: INPUT VALIDATION DISPLAY ---
with st.sidebar.form("new_ticket_panel", clear_on_submit=True):
    st.subheader("🆕 Open Operational Ticket")
    input_title = st.text_input("Brief Problem Statement Summary")
    input_author = st.text_input("Requester Corporate Email Address")
    submit_btn = st.form_submit_button("Launch Support Ticket Instance")
    
    if submit_btn:
        payload = {"title": input_title, "created_by": input_author}
        post_res = requests.post(f"{BACKEND_URL}/tickets", json=payload)
        if post_res.status_code == 200:
            st.success("Ticket pushed into operational state ledger!")
            st.rerun()
        else:
            # Displays the exact validation failure generated cleanly by Pydantic
            error_data = post_res.json()
            error_msg = error_data.get('detail', 'Unknown validation anomaly.')
            if isinstance(error_msg, list):  # Handle multiple Pydantic structural errors
                error_msg = error_msg[0].get('msg', 'Invalid inputs.')
            st.error(f"❌ Input Validation Refused: {error_msg}")

# Main Layout splitting
if not tickets:
    st.info("No matching tickets residing in active memory logs.")
else:
    options_map = {f"#{t['ticket_id']} | {t['title']} ({t['status'].upper()})": t for t in tickets}
    selected_key = st.selectbox("📂 Select Active Workspace Ticket Profile File Instance:", list(options_map.keys()))
    current_ticket = options_map[selected_key]
    
    st.divider()
    
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        st.subheader(f"Subject: {current_ticket['title']}")
        st.caption(f"Opened by: {current_ticket['created_by']} | Timestamp: {current_ticket['created_at']}")
    with c2:
        current_idx = ["open", "in_progress", "resolved"].index(current_ticket['status'])
        status_selector = st.selectbox("State Transition", ["open", "in_progress", "resolved"], index=current_idx)
        if st.button("Apply State Change"):
            requests.put(f"{BACKEND_URL}/tickets/{current_ticket['ticket_id']}/status", json={"status": status_selector})
            st.rerun()
            
    with c3:
        st.write("🛠️ Pipeline Destruction")
        # --- BONUS FEATURE: DELETE ACTION WITH CONFIRMATION STEP ---
        if f"confirm_delete_{current_ticket['ticket_id']}" not in st.session_state:
            st.session_state[f"confirm_delete_{current_ticket['ticket_id']}"] = False
            
        if not st.session_state[f"confirm_delete_{current_ticket['ticket_id']}"]:
            if st.button("🗑️ Delete Ticket Instance", key=f"del_init_{current_ticket['ticket_id']}"):
                st.session_state[f"confirm_delete_{current_ticket['ticket_id']}"] = True
                st.rerun()
        else:
            st.warning("⚠️ Are you sure?")
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("🔥 Yes, Delete", key=f"del_conf_{current_ticket['ticket_id']}"):
                    requests.delete(f"{BACKEND_URL}/tickets/{current_ticket['ticket_id']}")
                    st.session_state[f"confirm_delete_{current_ticket['ticket_id']}"] = False
                    st.success("Ticket dropped!")
                    st.rerun()
            with col_b2:
                if st.button("❌ Abort", key=f"del_abort_{current_ticket['ticket_id']}"):
                    st.session_state[f"confirm_delete_{current_ticket['ticket_id']}"] = False
                    st.rerun()

    # --- BONUS FEATURE: CHAT DESIGN UI OVERHAUL ---
    st.markdown("### 💬 Interactive Message Stream Threads")
    msg_res = requests.get(f"{BACKEND_URL}/tickets/{current_ticket['ticket_id']}/messages")
    messages_list = msg_res.json() if msg_res.status_code == 200 else []
    
    for message in messages_list:
        is_agent = "agent" in message['author'] or "admin" in message['author']
        with st.chat_message("assistant" if is_agent else "user"):
            st.markdown(f"**{message['author']}**")
            st.write(message['message_text'])
            st.caption(f"Time Record: {message['created_at']}")

    with st.form("append_message_form", clear_on_submit=True):
        st.write("✏️ Write Response Dispatch Log")
        reply_author = st.text_input("Responder Account ID Email")
        reply_text = st.text_area("Message Content Framework Context")
        submit_reply = st.form_submit_button("Transmit Message Frame")
        
        if submit_reply:
            msg_payload = {"message_text": reply_text, "author": reply_author}
            post_msg_res = requests.post(f"{BACKEND_URL}/tickets/{current_ticket['ticket_id']}/messages", json=msg_payload)
            if post_msg_res.status_code == 200:
                st.success("Message committed cleanly!")
                st.rerun()
            else:
                error_data = post_msg_res.json()
                msg_error = error_data.get('detail', 'Validation fault block error.')
                if isinstance(msg_error, list):
                    msg_error = msg_error[0].get('msg', 'Invalid inputs.')
                st.error(f"❌ Input Validation Refused: {msg_error}")
