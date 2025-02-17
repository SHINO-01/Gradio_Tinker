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
    
    # Create proper format for messages - clone the list to avoid reference issues
    updated_history = list(chat_history)
    updated_history.append({"role": "user", "content": user_text})
    updated_history.append({"role": "assistant", "content": bot_reply})
    
    return updated_history, ""

# Function to start a new chat (Saves previous chat properly)
def start_new_chat(selected_context, chat_history, session_list):
    if chat_history:  # Save previous chat if not empty
        chat_name = generate_chat_name()
        chat_sessions[chat_name] = list(chat_history)  # Store history
        session_list = list(session_list)
        session_list.append(chat_name)  # Add to session list
    
    # Clear chat and update available sessions
    welcome_message = f"🔄 New chat started with **{selected_context}** context!"
    
    # Create updated HTML for session list
    session_html = create_session_html(session_list)
    
    # Create initial chat with welcome message using correct message format
    new_chat = [{"role": "assistant", "content": welcome_message}]
    
    return new_chat, [], session_list, session_html

# Function to load a selected past chat
def load_chat(selected_index_str, session_list):
    try:
        selected_index = int(selected_index_str)
        if 0 <= selected_index < len(session_list):
            selected_chat = session_list[selected_index]
            if selected_chat in chat_sessions:
                return chat_sessions[selected_chat]
    except (ValueError, TypeError):
        pass
    return []  # Return empty list if anything goes wrong

# Function to create HTML for session list
def create_session_html(sessions):
    if not sessions:
        return "<div class='session-list'>No saved chats yet</div>"
    
    html = "<div class='session-list'>"
    for i, session in enumerate(sessions):
        # Create clickable divs with data attributes to store the index
        html += f"""
        <div class='session-item' onclick='selectSession({i})' data-index='{i}'>
            <div class='session-name'>{session}</div>
        </div>
        """
    html += "</div>"
    
    # Add styles and JavaScript for the sidebar
    html += """
    <style>
    .session-list {
        display: flex;
        flex-direction: column;
        gap: 8px;
        width: 100%;
        margin-top: 10px;
        color: #f0f0f0; /* Light text color for dark mode */
    }
    .session-item {
        padding: 10px;
        border-radius: 5px;
        background-color: #3a3a3a; /* Dark background for dark mode */
        cursor: pointer;
        transition: background-color 0.3s;
        color: #f0f0f0; /* Light text for dark background */
        border: 1px solid #4f4f4f; /* Subtle border */
    }
    .session-item:hover {
        background-color: #4a4a4a; /* Slightly lighter on hover */
    }
    .session-name {
        font-size: 14px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    </style>
    <script>
    function selectSession(index) {
        const sessionInput = document.querySelector('#session-select-callback');
        if (sessionInput) {
            sessionInput.value = index.toString();
            sessionInput.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }
    
    // Register this function to run when gradio is loaded
    if (window.gradio_config) {
        window.addEventListener('load', function() {
            // Force theme detection and reapply our styles
            applyDarkModeStyles();
        });
    } else {
        // If gradio_config isn't available yet, wait for it
        document.addEventListener('DOMContentLoaded', function() {
            applyDarkModeStyles();
        });
    }
    
    // Function to apply dark mode styles
    function applyDarkModeStyles() {
        const sessionItems = document.querySelectorAll('.session-item');
        sessionItems.forEach(item => {
            item.style.backgroundColor = '#3a3a3a';
            item.style.color = '#f0f0f0';
            item.style.border = '1px solid #4f4f4f';
        });
        
        // Style for no sessions message
        const sessionList = document.querySelector('.session-list');
        if (sessionList) {
            sessionList.style.color = '#f0f0f0';
        }
    }
    </script>
    """
    
    return html

# Gradio UI
with gr.Blocks(theme=gr.themes.Base(primary_hue="blue", neutral_hue="gray", text_size=gr.themes.sizes.text_md), css="""
    .sidebar {
        min-width: 250px;
        height: 100%;
        border-right: 1px solid #4f4f4f; /* Darker border for dark mode */
        padding-right: 10px;
        color: #f0f0f0; /* Light text for dark mode */
    }
    /* Force dark theme on button and chat elements */
    .new-chat-btn {
        background-color: #3a3a3a !important; 
        color: #f0f0f0 !important;
        border: 1px solid #4f4f4f !important;
    }
    .new-chat-btn:hover {
        background-color: #4a4a4a !important;
    }
""") as demo:
    with gr.Row():
        with gr.Column(scale=1, elem_classes=["sidebar"]):  # Sidebar
            gr.Markdown("## 📁 Chat History")

            # New Chat Button with dark mode styling
            new_chat_btn = gr.Button("➕ New Chat", elem_classes=["new-chat-btn"])

            # List of chat sessions (Sidebar)
            session_list = gr.State([])  # Stores chat session names
            
            # HTML component for clickable session list
            session_html = gr.HTML("<div class='session-list'>No saved chats yet</div>")
            
            # Hidden textbox to capture session selection via JavaScript
            session_select_callback = gr.Textbox(elem_id="session-select-callback", visible=False)

        with gr.Column(scale=4):  # Main Chat Interface
            gr.Markdown("# 🤖 Chatbot with RAG Embedding Context")

            # Dropdown for selecting embedding context
            context_selector = gr.Dropdown(
                choices=list(RAG_CONTEXTS.keys()),
                value="Science",
                label="Select Embedding Context"
            )

            # Chatbot UI (explicitly set type to messages)
            chatbot = gr.Chatbot(label="Chatbot", type="messages", avatar_images=["img1.png","img2.png"])

            # Create row for input and send button
            with gr.Row():
                # Multimodal Textbox (80% width)
                message_input = gr.MultimodalTextbox(
                    show_label=False, 
                    placeholder="Type your message here...",
                    file_types=[".pdf", ".txt"],
                    scale=9
                )
                
                # Send button (20% width)
                send_btn = gr.Button("Send", scale=1)

            # Hidden state to store chat history
            chat_history = gr.State([])

            # Function to handle sending messages
            def handle_message(user_input, history, context):
                new_history, _ = chatbot_response(user_input, history, context)
                return new_history, ""
                
            # Event: Handle send button click
            send_btn.click(
                handle_message,
                inputs=[message_input, chat_history, context_selector],
                outputs=[chatbot, message_input]
            ).then(
                lambda x: x,  # Identity function to pass through the chat history
                inputs=[chatbot],
                outputs=[chat_history]
            )
            
            # Event: Pressing 'Enter' in the input box
            message_input.submit(
                handle_message,
                inputs=[message_input, chat_history, context_selector],
                outputs=[chatbot, message_input]
            ).then(
                lambda x: x,  # Identity function to pass through the chat history
                inputs=[chatbot],
                outputs=[chat_history]
            )

            # Event: Change context resets chat history and starts a new chat
            context_selector.change(
                start_new_chat,
                inputs=[context_selector, chat_history, session_list],
                outputs=[chatbot, chat_history, session_list, session_html]
            )

            # Event: Clicking "New Chat" Button
            new_chat_btn.click(
                start_new_chat,
                inputs=[context_selector, chat_history, session_list],
                outputs=[chatbot, chat_history, session_list, session_html]
            )

            # Event: Handle session selection via hidden textbox
            session_select_callback.input(
                load_chat,
                inputs=[session_select_callback, session_list],
                outputs=[chatbot]
            ).then(
                lambda x: x,  # Identity function to pass through the chat history
                inputs=[chatbot],
                outputs=[chat_history]
            )
            
            # Initialize chat with welcome message
            demo.load(
                lambda: [{"role": "assistant", "content": "👋 Welcome! This chatbot is using the **Science** context."}],
                outputs=[chatbot]
            ).then(
                lambda x: x,
                inputs=[chatbot],
                outputs=[chat_history]
            )

demo.launch()