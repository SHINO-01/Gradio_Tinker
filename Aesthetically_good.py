import gradio as gr
import datetime

RAG_CONTEXTS = {
    "Science": "This chatbot specializes in answering science-related questions.",
    "History": "This chatbot provides insights into historical events and figures.",
    "Technology": "This chatbot discusses the latest advancements in technology.",
}

chat_sessions = {}

def generate_chat_name():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def chatbot_response(user_input, chat_history, selected_context):
    if isinstance(user_input, dict):
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

custom_css = """
/* === Global Reset to Fix Layout Issues === */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Inter', sans-serif; /* Clean modern font */
}

/* Ensure the body takes full width without overflow */
html, body {
    width: 100vw;
    height: 100vh;
    max-width: 100vw;
    max-height: 100vh;
    background-color: #0f172a; /* Dark theme */
    color: #f0f0f0;
    overflow-x: hidden;
    display: flex;
    justify-content: center;
}

/* === Main Layout Fix === */
.wrap.svelte-1byz9vf {
    flex-grow: 1;
    width: 100vw !important;
    max-width: 100vw !important;
    display: flex !important;
    justify-content: flex-start !important; /* Ensures no unwanted shifts */
    align-items: stretch !important;
    padding: 0; /* Resets unwanted padding */
    overflow-x: hidden !important; /* Ensures no overflow */
}

/* Fixes the parent flex container */
.contain.svelte-1byz9vf {
    display: flex !important;
    flex-grow: 1 !important;
    width: 100vw !important;
    max-width: 100vw !important;
    justify-content: flex-start !important;
    align-items: stretch !important;
    overflow-x: hidden !important;
    padding: 0 !important;
}

/* Ensures full width without overflow */
#main-row {
    display: flex !important;
    flex-grow: 1 !important;
    width: 100vw !important;
    max-width: 100vw !important;
    padding: 15px 20px; /* Adds some space without shifting */
    gap: 15px; /* Keeps sidebar and content spaced */
    overflow-x: hidden;
}

/* === Sidebar Styling === */
.sidebar {
    flex: 0 0 220px; /* Fixed width */
    height: 100%;
    background-color: #1e293b;
    padding: 20px;
    border-right: 2px solid #334155;
    display: flex;
    flex-direction: column;
    align-items: center;
    border-radius: 10px;
}

/* Sidebar Header */
.sidebar h2 {
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 20px;
}

/* New Chat Button */
.sidebar button {
    width: 100%;
    background-color: #3b82f6;
    color: white;
    border: none;
    padding: 12px;
    font-size: 14px;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s;
}

.sidebar button:hover {
    background-color: #2563eb;
}

/* === Chatbot Main Column Fix === */
.main-column {
    flex-grow: 1;
    width: calc(100vw - 240px) !important; /* Adjusts width correctly */
    max-width: calc(100vw - 240px) !important;
    padding: 20px;
    border-radius: 10px;
    background-color: #1e293b;
    overflow-x: hidden;
}

/* Chatbot Title */
.main-column h1 {
    font-size: 24px;
    font-weight: bold;
    text-align: center;
    margin-bottom: 20px;
}

/* Fixes Chatbot Container */
#component-11 {
    width: 100% !important;
    max-width: 100% !important;
    min-height: 500px;
    border-radius: 8px;
    background-color: #0f172a;
    padding: 15px;
    border: 1px solid #334155;
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
    overflow-x: hidden;
}

/* === Input Field Styling === */
#component-12 {
    display: flex;
    align-items: center;
    background-color: #334155;
    border-radius: 5px;
    padding: 10px;
    margin-top: 15px;
    overflow-x: hidden;
}

/* Message Input */
textarea[data-testid="textbox"] {

"""

with gr.Blocks(css=custom_css) as demo:
    with gr.Row(elem_id="main-row"):
        with gr.Column(scale=1, min_width=180, elem_classes=["sidebar"]):
            gr.Markdown("## 📁 Chat History")
            new_chat_btn = gr.Button("➕ New Chat")
            session_list = gr.State([])
            session_select_callback = gr.Textbox(visible=False, interactive=True)

        with gr.Column(scale=20, elem_classes=["main-column"]):
            gr.Markdown("# 🤖 Chatbot with RAG Embedding Context")

            context_selector = gr.Dropdown(
                choices=list(RAG_CONTEXTS.keys()),
                value="Science",
                label="Select Embedding Context"
            )

            chatbot = gr.Chatbot(label="Chatbot", type="messages", height=650, min_width="100%")

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

            new_chat_btn.click(lambda: [{"role": "assistant", "content": "🔄 New Chat Started!"}], outputs=[chatbot])

            demo.load(lambda: [{"role": "assistant", "content": "👋 Welcome! This chatbot uses the **Science** context."}], outputs=[chatbot])

demo.launch()
