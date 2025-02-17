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
        user_text = user_input  # Regular text input

    if not user_text.strip():
        return chat_history, ""  # Ignore empty messages

    context = RAG_CONTEXTS.get(selected_context, "General Chatbot")
    bot_reply = f"[{selected_context} Context] {context} - You asked: '{user_text}'"

    chat_history.append({"role": "user", "content": user_text})
    chat_history.append({"role": "assistant", "content": bot_reply})

    return chat_history, ""

# Function to start a new chat
def start_new_chat(selected_context, chat_history, session_list):
    if chat_history:  # Save previous chat if not empty
        chat_name = generate_chat_name()
        chat_sessions[chat_name] = list(chat_history)
        session_list.append(chat_name)  # Add to session list

    welcome_message = {
        "role": "assistant",
        "content": f"🔄 New chat started with **{selected_context}** context!"
    }
    session_html = create_session_html(session_list)

    return [welcome_message], [], session_list, session_html

# Function to load a selected past chat
def load_chat(selected_chat):
    if selected_chat in chat_sessions:
        print(f"🔍 DEBUG: Loading chat session: {selected_chat}")
        history = chat_sessions[selected_chat]
        print(f"✅ History Loaded: {history}")
        return history
    print(f"⚠️ No chat history found for {selected_chat}")
    return [{"role": "assistant", "content": "No history available for this session."}]

# JavaScript Code for Click Handling (Passed via `js` argument in `gr.Blocks`)
js_code = """
function selectSession(sessionName) {
    console.log("✅ DEBUG: Clicked session:", sessionName);
    const sessionInput = document.querySelector('#session-select-callback');
    if (sessionInput) {
        sessionInput.value = sessionName;
        sessionInput.dispatchEvent(new Event('input', { bubbles: true }));
        sessionInput.dispatchEvent(new Event('change', { bubbles: true }));
    }
}
"""

# Function to create HTML for session list
def create_session_html(sessions):
    if not sessions:
        return "<div class='session-list'>No saved chats yet</div>"

    html = "<div class='session-list'>"
    for session in sessions:
        html += f"""
        <div class='session-item' onclick="selectSession('{session}')" data-session="{session}">
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
    """
    return html

# Gradio UI (Passing `js` argument)
with gr.Blocks(js=js_code) as demo:
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

            message_input = gr.MultimodalTextbox(
                show_label=False, 
                placeholder="Type your message here...",
                file_types=[".pdf", ".txt"]
            )

            chat_history = gr.State([])

            message_input.submit(
                chatbot_response,
                inputs=[message_input, chat_history, context_selector],
                outputs=[chatbot, message_input]
            )

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

            session_select_callback.change(
                load_chat,
                inputs=[session_select_callback],
                outputs=[chatbot]
            )

            demo.load(lambda: [{"role": "assistant", "content": "👋 Welcome! This chatbot is using the **Science** context."}], outputs=[chatbot])

demo.launch()
