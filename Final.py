import gradio as gr
import datetime
import json

# Simulated RAG Embedding Contexts
RAG_CONTEXTS = {
    "Science": "This chatbot specializes in answering science-related questions.",
    "History": "This chatbot provides insights into historical events and figures.",
    "Technology": "This chatbot discusses the latest advancements in technology.",
}

# Global storage for saved chat sessions
chat_sessions = {}

# Function to generate a unique chat session name
def generate_chat_name():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Chatbot response function (handles multimodal input)
def chatbot_response(user_input, chat_history, selected_context):
    user_text = user_input.get("text", "") if isinstance(user_input, dict) else user_input

    if not user_text.strip():
        return chat_history, ""  # Ignore empty messages

    context = RAG_CONTEXTS.get(selected_context, "General Chatbot")
    bot_reply = f"[{selected_context} Context] {context} - You asked: '{user_text}'"
    
    updated_history = list(chat_history)
    updated_history.append({"role": "user", "content": user_text})
    updated_history.append({"role": "assistant", "content": bot_reply})
    
    return updated_history, ""

# Function to select a session
def select_session_backend(index_str, sessions):
    try:
        index = int(index_str)
        if 0 <= index < len(sessions):
            selected_chat = sessions[index]
            if selected_chat in chat_sessions:
                return chat_sessions[selected_chat], chat_sessions[selected_chat]
        return [], []
    except:
        return [], []

# Function to start a new chat
def start_new_chat(selected_context, chat_history, session_list):
    if chat_history:
        chat_name = generate_chat_name()
        chat_sessions[chat_name] = list(chat_history)
        session_list = list(session_list)
        session_list.append(chat_name)
    
    welcome_message = f"🔄 New chat started with **{selected_context}** context!"
    session_html = create_session_html(session_list)
    new_chat = [{"role": "assistant", "content": welcome_message}]
    
    return new_chat, [], session_list, session_html

# Function to create session list HTML
def create_session_html(sessions):
    if not sessions:
        return "<div class='session-list'>No saved chats yet</div>"

    html = "<div class='session-list'>"
    for i, session in enumerate(sessions):
        html += f"""
        <div class='session-item' data-index='{i}'>
            <div class='session-name'>{session}</div>
        </div>
        """
    html += "</div>"
    return html

# Gradio UI
with gr.Blocks(css="""
    .sidebar {
        min-width: 250px;
        height: 100%;
        border-right: 1px solid #4f4f4f;
        padding-right: 10px;
        color: #f0f0f0;
    }
    .new-chat-btn {
        background-color: #3a3a3a !important; 
        color: #f0f0f0 !important;
        border: 1px solid #4f4f4f !important;
    }
    .new-chat-btn:hover {
        background-color: #4a4a4a !important;
    }
""") as demo:
    gr.HTML("<script src='custom.js'></script>")
    with gr.Row():
        with gr.Column(scale=1, elem_classes=["sidebar"]):  # Sidebar
            gr.Markdown("## 📁 Chat History")
            new_chat_btn = gr.Button("➕ New Chat", elem_classes=["new-chat-btn"])
            session_list = gr.State([])
            session_select_callback = gr.Textbox(elem_id="session-select-callback", visible=False)
            session_html = gr.HTML("<div class='session-list'>No saved chats yet</div>")

        with gr.Column(scale=4):  # Main Chat Interface
            gr.Markdown("# 🤖 Chatbot with RAG Embedding Context")
            context_selector = gr.Dropdown(choices=list(RAG_CONTEXTS.keys()), value="Science", label="Select Embedding Context")
            chatbot = gr.Chatbot(label="Chatbot", type="messages")

            with gr.Row():
                message_input = gr.MultimodalTextbox(show_label=False, placeholder="Type your message here...", file_types=[".pdf", ".txt"], scale=9)
                send_btn = gr.Button("Send", scale=1)

            chat_history = gr.State([])

            def handle_message(user_input, history, context):
                new_history, _ = chatbot_response(user_input, history, context)
                return new_history, ""

            send_btn.click(handle_message, inputs=[message_input, chat_history, context_selector], outputs=[chatbot, message_input]).then(
                lambda x: x, inputs=[chatbot], outputs=[chat_history]
            )

            message_input.submit(handle_message, inputs=[message_input, chat_history, context_selector], outputs=[chatbot, message_input]).then(
                lambda x: x, inputs=[chatbot], outputs=[chat_history]
            )

            context_selector.change(start_new_chat, inputs=[context_selector, chat_history, session_list], outputs=[chatbot, chat_history, session_list, session_html])

            new_chat_btn.click(start_new_chat, inputs=[context_selector, chat_history, session_list], outputs=[chatbot, chat_history, session_list, session_html])

            def select_and_load_session(index_str):
                return select_session_backend(index_str, session_list.value)

            demo.load(select_and_load_session, inputs=[session_select_callback], outputs=[chatbot, chat_history])

            demo.load(lambda: [{"role": "assistant", "content": "👋 Welcome! This chatbot is using the **Science** context."}], outputs=[chatbot]).then(
                lambda x: x, inputs=[chatbot], outputs=[chat_history]
            )

demo.launch()
