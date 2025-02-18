import gradio as gr
import datetime

# --- Simulated RAG Embedding Contexts ---
RAG_CONTEXTS = {
    "Science": "This chatbot specializes in answering science-related questions.",
    "History": "This chatbot provides insights into historical events and figures.",
    "Technology": "This chatbot discusses the latest advancements in technology.",
}

# Global storage for saved chat sessions
chat_sessions = {}

# Generate a unique chat session name based on current time
def generate_chat_name():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# -------------------------------
# Chatbot response function
# (handles multimodal input)
# -------------------------------
def chatbot_response(user_input, chat_history, selected_context):
    print(f"[DEBUG] chatbot_response() called with user_input={user_input} selected_context={selected_context}")
    
    if isinstance(user_input, dict):  # e.g., user uploaded a file
        user_text = user_input.get("text", "")
    else:
        user_text = user_input  # Regular text
    
    if not user_text.strip():
        print("[DEBUG] Empty user input; ignoring.")
        return chat_history, ""  # Ignore empty messages

    context = RAG_CONTEXTS.get(selected_context, "General Chatbot")
    bot_reply = f"[{selected_context} Context] {context} - You asked: '{user_text}'"
    
    updated_history = list(chat_history)
    updated_history.append({"role": "user", "content": user_text})
    updated_history.append({"role": "assistant", "content": bot_reply})
    
    return updated_history, ""

# -------------------------------------------
# Start new chat, optionally save old one
# -------------------------------------------
def start_new_chat(selected_context, chat_history, session_list):
    print(f"[DEBUG] start_new_chat() triggered with context={selected_context}, len(chat_history)={len(chat_history)}")
    
    if chat_history:
        # Save the previous session if it's not empty
        chat_name = generate_chat_name()
        chat_sessions[chat_name] = list(chat_history)
        
        session_list = list(session_list)
        session_list.append(chat_name)

        print(f"[DEBUG] Saved previous session as '{chat_name}' with {len(chat_history)} messages")

    welcome_message = f"🔄 New chat started with **{selected_context}** context!"
    
    # Update session list HTML
    session_html = create_session_html(session_list)
    
    # Start fresh chat (assistant message only)
    new_chat = [{"role": "assistant", "content": welcome_message}]
    
    return new_chat, [], session_list, session_html

# ---------------------------------------------
# Load a past chat by index from 'session_list'
# ---------------------------------------------
def load_chat(selected_index_str, session_list):
    print(f"[DEBUG] load_chat() triggered with selected_index_str={selected_index_str}")
    try:
        selected_index = int(selected_index_str)
        if 0 <= selected_index < len(session_list):
            selected_chat_name = session_list[selected_index]
            print(f"[DEBUG] Attempting to load chat session '{selected_chat_name}'")
            if selected_chat_name in chat_sessions:
                return chat_sessions[selected_chat_name]
    except (ValueError, TypeError):
        pass
    print("[DEBUG] Invalid session index or chat not found. Returning empty list.")
    return []  # return empty if invalid selection

# ---------------------------------------------
# Dynamically build HTML to show past sessions
# ---------------------------------------------
def create_session_html(sessions):
    print(f"[DEBUG] create_session_html() called. sessions={sessions}")
    
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
    
    # Minimal CSS included inline for convenience
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
    """
    return html

# ----------------------------------------------
# Event Delegation Script in <head>
# - Attaches one click listener to document
# - If .session-item is clicked, it triggers the hidden textbox
# ----------------------------------------------
custom_js = """
<script>
console.log("[DEBUG] Custom JS loaded. Attaching event delegation for session items...");

window.addEventListener("load", () => {
  console.log("[DEBUG] window.load event fired. Delegating clicks...");

  document.addEventListener("click", (event) => {
    // .closest() finds the nearest parent with the class .session-item
    const item = event.target.closest(".session-item");
    if (!item) return; // Not clicked on a .session-item

    const index = item.getAttribute("data-index");
    console.log("[DEBUG] Clicked on .session-item with index:", index);

    if (index !== null) {
      const sessionInput = document.querySelector("#session-select-callback");
      if (sessionInput) {
        sessionInput.value = index;
        // Dispatch 'input' so Gradio sees the change
        sessionInput.dispatchEvent(new Event("input", { bubbles: true }));
      } else {
        console.log("[DEBUG] #session-select-callback not found!");
      }
    }
  });
});
</script>
"""

# =============================================
#        Gradio UI Setup with Blocks
# =============================================
with gr.Blocks(
    head=custom_js,  # <--- Injecting script into <head>
    theme=gr.themes.Base(primary_hue="blue", neutral_hue="gray", text_size=gr.themes.sizes.text_md),
    css="""
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
"""
) as demo:
    with gr.Row():
        # ----------------------
        # Sidebar
        # ----------------------
        with gr.Column(scale=1, elem_classes=["sidebar"]):
            gr.Markdown("## 📁 Chat History")

            new_chat_btn = gr.Button("➕ New Chat", elem_classes=["new-chat-btn"])
            session_list = gr.State([])  
            session_html = gr.HTML("<div class='session-list'>No saved chats yet</div>")
            
            # Hidden textbox to capture session selection
            session_select_callback = gr.Textbox(elem_id="session-select-callback", visible=False)

        # ----------------------
        # Main Chat UI
        # ----------------------
        with gr.Column(scale=4):
            gr.Markdown("# 🤖 Chatbot with RAG Embedding Context")

            context_selector = gr.Dropdown(
                choices=list(RAG_CONTEXTS.keys()),
                value="Science",
                label="Select Embedding Context"
            )

            chatbot = gr.Chatbot(
                label="Chatbot",
                type="messages",
                avatar_images=["img1.png", "img2.png"]  
            )

            with gr.Row():
                message_input = gr.MultimodalTextbox(
                    show_label=False, 
                    placeholder="Type your message here...",
                    file_types=[".pdf", ".txt"],
                    scale=9
                )
                send_btn = gr.Button("Send", scale=1)

            chat_history = gr.State([])

            # Handler for sending messages
            def handle_message(user_input, history, context):
                print("[DEBUG] handle_message() triggered.")
                new_history, _ = chatbot_response(user_input, history, context)
                return new_history, ""

            # Send button
            send_chain = send_btn.click(
                handle_message,
                inputs=[message_input, chat_history, context_selector],
                outputs=[chatbot, message_input]
            )
            send_chain.then(
                lambda x: x,
                inputs=[chatbot],
                outputs=[chat_history]
            )

            # Pressing Enter in the input
            enter_chain = message_input.submit(
                handle_message,
                inputs=[message_input, chat_history, context_selector],
                outputs=[chatbot, message_input]
            )
            enter_chain.then(
                lambda x: x,
                inputs=[chatbot],
                outputs=[chat_history]
            )

            # Changing context => start new chat
            context_selector.change(
                start_new_chat,
                inputs=[context_selector, chat_history, session_list],
                outputs=[chatbot, chat_history, session_list, session_html]
            )

            # "New Chat" button
            new_chat_btn.click(
                start_new_chat,
                inputs=[context_selector, chat_history, session_list],
                outputs=[chatbot, chat_history, session_list, session_html]
            )

            # Handle session selection from hidden textbox
            session_select_callback.input(
                load_chat,
                inputs=[session_select_callback, session_list],
                outputs=[chatbot]
            ).then(
                lambda x: x,
                inputs=[chatbot],
                outputs=[chat_history]
            )

            # On initial load, show a default welcome
            load_chain = demo.load(
                lambda: [{"role": "assistant", "content": "👋 Welcome! This chatbot is using the **Science** context."}],
                outputs=[chatbot]
            )
            load_chain.then(
                lambda x: x,
                inputs=[chatbot],
                outputs=[chat_history]
            )

demo.launch()
