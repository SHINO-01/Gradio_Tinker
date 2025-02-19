import gradio as gr
import datetime

# === Simulated RAG Embedding Contexts ===
RAG_CONTEXTS = {
    "Science": "This chatbot specializes in answering science-related questions.",
    "History": "This chatbot provides insights into historical events and figures.",
    "Technology": "This chatbot discusses the latest advancements in technology.",
}

chat_sessions = {}

def generate_chat_name():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def chatbot_response(user_input, chat_history, selected_context):
    if isinstance(user_input, dict):  # Handles multimodal input
        user_text = user_input.get("text", "")
    else:
        user_text = user_input

    if not user_text.strip():
        return chat_history, ""

    context_description = RAG_CONTEXTS.get(selected_context, "General Chatbot")
    bot_reply = f"[{selected_context} Context] {context_description} - You asked: '{user_text}'"

    updated_history = list(chat_history)
    updated_history.append({"role": "user", "content": user_text})
    updated_history.append({"role": "assistant", "content": bot_reply})

    return updated_history, ""

def start_new_chat(selected_context, chat_history, session_list):
    if chat_history:
        chat_name = generate_chat_name()
        chat_sessions[chat_name] = list(chat_history)
        session_list.append(chat_name)

    welcome_message = f"🔄 New chat started with **{selected_context}** context!"
    return [{"role": "assistant", "content": welcome_message}], [], session_list

def load_chat(selected_index_str, session_list):
    try:
        idx = int(selected_index_str)
        if 0 <= idx < len(session_list):
            chat_name = session_list[idx]
            if chat_name in chat_sessions:
                return chat_sessions[chat_name]
    except (ValueError, TypeError):
        pass
    return []

custom_css = """
.main-row {
    display: flex !important;
    flex-grow: 1 !important;
    width: 100% !important;
}

.gradio-container {
    max-width: 100vw !important;
    height: 100vh !important;
    padding: 0 !important;
    background: #0f172a !important;
    display: flex;
    flex-direction: column;
}

.sidebar {
    flex: 0 0 220px !important;
    height: 100%;
    border-right: 1px solid #4f4f4f;
    padding-right: 10px;
    color: #f0f0f0;
}

.main-column {
    flex: 1 !important;
}
"""

with gr.Blocks(css=custom_css) as demo:
    with gr.Row(elem_id="main-row"):
        # -------------- Sidebar --------------
        with gr.Column(scale=1, min_width=220, elem_classes=["sidebar"]):
            gr.Markdown("## 📁 Chat History")
            new_chat_btn = gr.Button("➕ New Chat")
            session_list = gr.State([])
            session_select_callback = gr.Textbox(visible=False, interactive=True)

        # -------------- Main Chat UI --------------
        with gr.Column(scale=20, min_width=1000, elem_classes=["main-column"]):
            gr.Markdown("# 🤖 Chatbot with RAG Embedding Context")

            context_selector = gr.Dropdown(
                choices=list(RAG_CONTEXTS.keys()),
                value="Science",
                label="Select Embedding Context"
            )

            chatbot = gr.Chatbot(label="Chatbot", type="messages", height=650, min_width=1200)

            with gr.Row():
                message_input = gr.MultimodalTextbox(
                    show_label=False, placeholder="Type your message here...", scale=12
                )
                send_btn = gr.Button("Send", scale=2)

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

            context_selector.change(start_new_chat, inputs=[context_selector, chat_history, session_list], outputs=[chatbot, chat_history, session_list])

            new_chat_btn.click(start_new_chat, inputs=[context_selector, chat_history, session_list], outputs=[chatbot, chat_history, session_list])

            session_select_callback.input(load_chat, inputs=[session_select_callback, session_list], outputs=[chatbot]).then(
                lambda x: x, inputs=[chatbot], outputs=[chat_history]
            )

            demo.load(lambda: [{"role": "assistant", "content": "👋 Welcome! This chatbot uses the **Science** context."}], outputs=[chatbot]).then(
                lambda x: x, inputs=[chatbot], outputs=[chat_history]
            )

demo.launch()
