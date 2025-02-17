import gradio as gr
import datetime

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

# Chatbot response function
def chatbot_response(user_input, chat_history, selected_context):
    if isinstance(user_input, dict):  # Handle multimodal input
        user_text = user_input.get("text", "")
    else:
        user_text = user_input
    
    if not user_text.strip():
        return chat_history, ""

    context = RAG_CONTEXTS.get(selected_context, "General Chatbot")
    bot_reply = f"[{selected_context} Context] {context} - You asked: '{user_text}'"

    updated_history = list(chat_history)
    updated_history.append({"role": "user", "content": user_text})
    updated_history.append({"role": "assistant", "content": bot_reply})
    
    return updated_history, ""

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

# Function to load a selected past chat
def load_chat(selected_chat_name):
    return chat_sessions.get(selected_chat_name, [])

# Function to create HTML for session list
def create_session_html(sessions):
    if not sessions:
        return "<div class='session-list'>No saved chats yet</div>"

    html = "<div class='session-list'>"
    for session in sessions:
        html += f"""
        <div class='session-item' onclick="selectSession('{session}')">
            <div class='session-name'>{session}</div>
        </div>
        """
    html += "</div>"

    html += """
    <style>
    .session-list {
        display: flex;
        flex-direction: column;
        gap: 8px;
        width: 100%;
        margin-top: 10px;
        color: #f0f0f0;
    }
    .session-item {
        padding: 10px;
        border-radius: 5px;
        background-color: #3a3a3a;
        cursor: pointer;
        transition: background-color 0.3s;
        color: #f0f0f0;
        border: 1px solid #4f4f4f;
    }
    .session-item:hover {
        background-color: #4a4a4a;
    }
    </style>
    <script>
    window.selectSession = function(sessionName) {
        const sessionInput = document.querySelector('#session-select-callback');
        if (sessionInput) {
            sessionInput.value = sessionName;
            sessionInput.dispatchEvent(new Event('input', { bubbles: true }));
            sessionInput.dispatchEvent(new Event('change', { bubbles: true }));
        }
    };
    </script>
    """
    return html

# Gradio UI
with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("## 📁 Chat History")
            new_chat_btn = gr.Button("➕ New Chat")
            session_list = gr.State([])  
            session_html = gr.HTML("<div class='session-list'>No saved chats yet</div>")
            session_select_callback = gr.Textbox(elem_id="session-select-callback", visible=False)

        with gr.Column(scale=4):  
            gr.Markdown("# 🤖 Chatbot with RAG Embedding Context")

            context_selector = gr.Dropdown(
                choices=list(RAG_CONTEXTS.keys()),
                value="Science",
                label="Select Embedding Context"
            )

            chatbot = gr.Chatbot(label="Chatbot", type="messages")

            with gr.Row():
                message_input = gr.MultimodalTextbox(
                    show_label=False, 
                    placeholder="Type your message here...",
                    file_types=[".pdf", ".txt"],
                    scale=9
                )
                send_btn = gr.Button("Send", scale=1)

            chat_history = gr.State([])

            def handle_message(user_input, history, context):
                new_history, _ = chatbot_response(user_input, history, context)
                return new_history, ""

            send_btn.click(
                handle_message,
                inputs=[message_input, chat_history, context_selector],
                outputs=[chatbot, message_input]
            ).then(lambda x: x, inputs=[chatbot], outputs=[chat_history])

            message_input.submit(
                handle_message,
                inputs=[message_input, chat_history, context_selector],
                outputs=[chatbot, message_input]
            ).then(lambda x: x, inputs=[chatbot], outputs=[chat_history])

            context_selector.change(
                start_new_chat,
                inputs=[context_selector, chat_history, session_list],
                outputs=[chatbot, chat_history, session_list, session_html]
            )

            new_chat_btn.click(
                start_new_chat,
                inputs=[context_selector, chat_history, session_list],
                outputs=[chatbot, chat_history, session_list, session_html]
            )

            session_select_callback.input(
                load_chat,
                inputs=[session_select_callback],
                outputs=[chatbot]
            ).then(lambda x: x, inputs=[chatbot], outputs=[chat_history])

            demo.load(
                lambda: [{"role": "assistant", "content": "👋 Welcome! This chatbot is using the **Science** context."}],
                outputs=[chatbot]
            ).then(lambda x: x, inputs=[chatbot], outputs=[chat_history])

demo.launch()
