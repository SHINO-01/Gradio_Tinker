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
/* Global reset to ensure no unnecessary margins or padding */
* {
    margin: 0 !important;
    padding: 0 !important;
    box-sizing: border-box !important;
}

/* Force the body and HTML to use full width */
html, body {
    width: 100vw !important;
    max-width: 100vw !important;
    overflow-x: hidden !important;
}

/* Force .wrap to fully expand */
.wrap.svelte-1byz9vf {
    flex-grow: 1 !important;
    width: 100vw !important;
    max-width: 100vw !important;
    display: flex !important;
    justify-content: flex-start !important; /* Prevents shifting */
    align-items: stretch !important;
    overflow-x: hidden !important;
}

/* Ensure parent container allows full expansion */
.contain.svelte-1byz9vf {
    display: flex !important;
    flex-grow: 1 !important;
    width: 100vw !important;
    max-width: 100vw !important;
    justify-content: flex-start !important;
    align-items: stretch !important;
    overflow-x: hidden !important;
}

/* Force all row-based layouts to use full width */
#main-row {
    display: flex !important;
    flex-grow: 1 !important;
    width: 100vw !important;
    max-width: 100vw !important;
    overflow-x: hidden !important;
}

/* Fix the column containing .wrap */
#component-0.column.svelte-vt1mxs {
    flex-grow: 1 !important;
    width: 100vw !important;
    max-width: 100vw !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Force the chatbot container to never overflow */
#component-11 {
    width: 100vw !important;
    max-width: 100vw !important;
    overflow-x: hidden !important;
    display: flex !important;
    flex-direction: column !important;
}

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
