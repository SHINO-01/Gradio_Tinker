import gradio as gr
import datetime

# Simulated RAG Embedding Contexts
RAG_CONTEXTS = {
    "Science": "This chatbot specializes in answering science-related questions.",
    "History": "This chatbot provides insights into historical events and figures.",
    "Technology": "This chatbot discusses the latest advancements in technology.",
}

# Global storage for chat sessions
chat_sessions = {}

# Function to generate a unique chat session name
def generate_chat_name():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Chatbot response function
def chatbot_response(user_input, chat_history, selected_context):
    if isinstance(user_input, dict):  # Handle multimodal input (text + file)
        user_text = user_input.get("text", "")
    else:
        user_text = user_input  # Regular text input
    
    if not user_text.strip():
        return chat_history, ""  # Ignore empty messages

    context = RAG_CONTEXTS.get(selected_context, "General Chatbot")
    bot_reply = f"[{selected_context} Context] {context} - You asked: '{user_text}'"

    # Convert history to expected message format
    chat_history.append({"role": "user", "content": user_text})
    chat_history.append({"role": "assistant", "content": bot_reply})

    return chat_history, ""

# Function to update the sidebar (Generate clickable chat history links)
def update_sidebar(session_list):
    if not session_list:
        return "### 📝 Chat History\n\n*No previous chats yet.*"
    
    markdown_text = "### 📝 Chat History\n\n"
    for chat_name in session_list:
        markdown_text += f"- `{chat_name}`\n"
    return markdown_text

# ✅ Function to start a new chat and ensure all components reset properly
def start_new_chat(selected_context, chat_history, session_list):
    # ✅ Save previous chat session if not empty
    if chat_history and len(chat_history) > 0:
        chat_name = generate_chat_name()
        chat_sessions[chat_name] = chat_history.copy()  # Store previous chat session
        session_list.append(chat_name)

    # ✅ **Fully reset chat history**
    chat_history.clear()  # Clear previous chat in memory
    chat_history = []  # Reassign to a new empty list

    # ✅ **Force UI update with a double refresh trick**
    return (
        gr.update(value=[]),  # Clears chatbot UI
        gr.update(value=""),  # Clears text input field
        gr.State([]),  # Properly resets chat history
        session_list,  # Updates session list
        update_sidebar(session_list),  # Updates sidebar
        gr.update(value="")  # Clears selected chat
    )

# Function to load a selected past chat
def load_chat(selected_chat):
    chat_name = selected_chat.strip()
    return chat_sessions.get(chat_name, [])

# Gradio UI
with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column(scale=1, min_width=250):  # Sidebar
            gr.Markdown("## 📁 Chat History")

            # New Chat Button
            new_chat_btn = gr.Button("➕ New Chat")

            # Sidebar for chat history (Clickable text)
            chat_list = gr.State([])  # Stores list of chat names
            chat_history_sidebar = gr.Markdown("### 📝 Chat History\n\n*No previous chats yet.*")

            # State for storing selected chat (Prevents looping)
            selected_chat = gr.State("")

        with gr.Column(scale=4):  # Main Chat Interface
            gr.Markdown("# 🤖 Chatbot with RAG Embedding Context")

            # Dropdown for selecting embedding context
            context_selector = gr.Dropdown(
                choices=list(RAG_CONTEXTS.keys()),
                value="Science",
                label="Select Embedding Context"
            )

            # Chatbot UI (Fix: `type="messages"` needs formatted data)
            chatbot = gr.Chatbot(label="Chatbot", type="messages")

            # Multimodal Textbox (Fixing text extraction issue)
            message_input = gr.MultimodalTextbox(
                show_label=False, 
                placeholder="Type your message here...",
                file_types=[".pdf", ".txt"]
            )

            # Hidden state to store chat history
            chat_history = gr.State([])

            # Event: Pressing 'Enter' sends the message (Fixes format issue)
            message_input.submit(
                chatbot_response,
                inputs=[message_input, chat_history, context_selector],
                outputs=[chatbot, message_input]
            )

            # Event: Change context resets chat history and starts a new chat
            context_selector.change(
                start_new_chat,
                inputs=[context_selector, chat_history, chat_list],
                outputs=[chatbot, message_input, chat_history, chat_list, chat_history_sidebar, selected_chat]
            )

            # Event: Clicking "New Chat" Button
            new_chat_btn.click(
                start_new_chat,
                inputs=[context_selector, chat_history, chat_list],
                outputs=[chatbot, message_input, chat_history, chat_list, chat_history_sidebar, selected_chat]
            )

            # Function: Extract chat name when clicked in sidebar
            def extract_chat_name(markdown_text, session_list):
                for chat in session_list:
                    if chat in markdown_text:
                        return chat  # Extract the most recent clicked chat
                return ""

            # Event: Clicking a past chat updates the selected chat
            chat_history_sidebar.change(
                extract_chat_name,
                inputs=[chat_history_sidebar, chat_list],
                outputs=[selected_chat]
            )

            # Event: Loading a selected chat
            selected_chat.change(
                load_chat,
                inputs=[selected_chat],
                outputs=[chatbot]
            )

demo.launch()
