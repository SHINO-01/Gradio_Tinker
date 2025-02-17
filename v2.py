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

# Chatbot response function (handles multimodal input)
def chatbot_response(user_input, chat_history, selected_context):
    if isinstance(user_input, dict):  # Handle multimodal input (text + file)
        user_text = user_input.get("text", "")
    else:
        user_text = user_input  # Regular text input
    
    if not user_text.strip():
        return chat_history, ""  # Ignore empty messages

    context = RAG_CONTEXTS.get(selected_context, "General Chatbot")
    bot_reply = f"[{selected_context} Context] {context} - You asked: '{user_text}'"

    # Ensure messages follow Gradio's expected format
    chat_history.append({"role": "user", "content": user_text})
    chat_history.append({"role": "assistant", "content": bot_reply})

    return chat_history, ""

# Function to start a new chat (Saves previous chat properly)
def start_new_chat(selected_context, chat_history, session_list, session_dropdown):
    if chat_history:  # Save previous chat if not empty
        chat_name = generate_chat_name()
        chat_sessions[chat_name] = list(chat_history)  # Store history
        session_list.append(chat_name)  # Add to session list
    
    # Clear chat and update available sessions
    welcome_message = {
        "role": "assistant",
        "content": f"🔄 New chat started with **{selected_context}** context!"
    }
    updated_sessions = list(session_list)  # Ensure Gradio sees the change
    return [welcome_message], [], updated_sessions, gr.Dropdown(choices=updated_sessions, label="Previous Chats")

# Function to load a selected past chat
def load_chat(selected_chat):
    if selected_chat in chat_sessions:
        return chat_sessions[selected_chat]
    return []

# Gradio UI
with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column(scale=1, min_width=250):  # Sidebar
            gr.Markdown("## 📁 Chat History")

            # New Chat Button
            new_chat_btn = gr.Button("➕ New Chat")

            # List of chat sessions (Sidebar)
            session_list = gr.State([])  # Stores chat session names
            session_dropdown = gr.Dropdown(choices=[], label="Previous Chats", interactive=True)

        with gr.Column(scale=4):  # Main Chat Interface
            gr.Markdown("# 🤖 Chatbot with RAG Embedding Context")

            # Dropdown for selecting embedding context
            context_selector = gr.Dropdown(
                choices=list(RAG_CONTEXTS.keys()),
                value="Science",
                label="Select Embedding Context"
            )

            # Chatbot UI
            chatbot = gr.Chatbot(label="Chatbot", type="messages")

            # Multimodal Textbox (Fixing text extraction issue)
            message_input = gr.MultimodalTextbox(
                show_label=False, 
                placeholder="Type your message here...",
                file_types=[".pdf", ".txt"]
            )

            # Hidden state to store chat history
            chat_history = gr.State([])

            # Event: Pressing 'Enter' sends the message
            message_input.submit(
                chatbot_response,
                inputs=[message_input, chat_history, context_selector],
                outputs=[chatbot, message_input]
            )

            # Event: Change context resets chat history and starts a new chat
            context_selector.change(
                start_new_chat,
                inputs=[context_selector, chat_history, session_list, session_dropdown],
                outputs=[chatbot, chat_history, session_list, session_dropdown]
            )

            # Event: Clicking "New Chat" Button
            new_chat_btn.click(
                start_new_chat,
                inputs=[context_selector, chat_history, session_list, session_dropdown],
                outputs=[chatbot, chat_history, session_list, session_dropdown]
            )

            # Event: Selecting a past chat loads it
            session_dropdown.change(
                load_chat,
                inputs=[session_dropdown],
                outputs=[chatbot]
            )
            
demo.launch()
