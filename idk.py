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
/* === Reset Everything for a Clean Layout === */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Inter', sans-serif;
}

/* === Ensure Full-Screen View Without Overflow === */
html, body {
    width: 100vw;
    height: 100vh;
    max-width: 100vw;
    max-height: 100vh;
    background-color: #0f172a;
    color: #f0f0f0;
    overflow-x: hidden;
    display: flex;
}

/* === Fix .wrap to Use Full Width & Add Spacing === */
.wrap.svelte-1byz9vf {
    flex-grow: 1;
    width: 100vw;
    max-width: 100vw;
    display: flex;
    justify-content: flex-start;
    align-items: stretch;
    padding: 10px 20px; /* Added spacing */
    overflow-x: hidden;
}

/* === Ensure Main Row Uses Full Width & Add Padding === */
#main-row {
    display: flex;
    flex-grow: 1;
    width: 100vw;
    max-width: 100vw;
    padding: 20px 25px; /* Adds comfortable space */
    gap: 20px; /* Keeps sidebar and main UI spaced properly */
    overflow-x: hidden;
}

/* === Sidebar: Fixed Width with Comfortable Padding === */
.sidebar {
    flex: 0 0 220px;
    height: 100vh;
    background-color: #1e293b;
    padding: 25px 20px; /* Balanced space inside */
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

/* === Main Chatbot Column: Takes Remaining Space with Padding === */
.main-column {
    flex-grow: 1;
    width: calc(100vw - 250px); /* Keeps it within the viewport */
    max-width: calc(100vw - 250px);
    padding: 25px;
    border-radius: 10px;
    background-color: #1e293b;
    overflow-x: hidden;
}

/* === Chatbot Container: Adds Margins & Rounded Borders === */
#component-11 {
    width: 100%;
    max-width: 100%;
    min-height: 550px; /* Slightly bigger */
    border-radius: 12px; /* More rounded */
    background-color: #0f172a;
    padding: 20px; /* Adds padding inside */
    border: 1px solid #334155;
    box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.3); /* Softer shadow */
    overflow-x: hidden;
}

/* === Input Field Styling (Spacing & Alignment) === */
#component-12 {
    display: flex;
    align-items: center;
    background-color: #334155;
    border-radius: 5px;
    padding: 12px;
    margin-top: 20px; /* Space between chat and input */
    overflow-x: hidden;
}

/* === Message Input Box === */
textarea[data-testid="textbox"] {
    flex-grow: 1;
    background-color: transparent;
    border: none;
    outline: none;
    color: white;
    font-size: 16px;
    padding: 12px;
}

/* === Send Button (More Padding & Aesthetic Hover Effect) === */
button.submit-button {
    background-color: #3b82f6;
    border: none;
    padding: 12px 18px; /* Increased padding */
    font-size: 16px;
    color: white;
    border-radius: 5px;
    cursor: pointer;
    transition: all 0.3s ease-in-out;
}

button.submit-button:hover {
    background-color: #2563eb;
    transform: scale(1.05);
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
