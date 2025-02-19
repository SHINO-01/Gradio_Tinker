import gradio as gr
import datetime

# === Simulated RAG Embedding Contexts ===
RAG_CONTEXTS = {
    "Science": "This chatbot specializes in answering science-related questions.",
    "History": "This chatbot provides insights into historical events and figures.",
    "Technology": "This chatbot discusses the latest advancements in technology.",
}

# Global storage for saved chat sessions
chat_sessions = {}

# Generate a unique chat session name
def generate_chat_name():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# -------------------------------
# Chatbot response function
# (handles multimodal input too)
# -------------------------------
def chatbot_response(user_input, chat_history, selected_context):
    print("[DEBUG] chatbot_response() called with user_input=", user_input, " context=", selected_context)

    if isinstance(user_input, dict):  # e.g., user uploaded a file
        user_text = user_input.get("text", "")
    else:
        user_text = user_input.strip()

    if not user_text:
        print("[DEBUG] Empty user input. Ignoring.")
        return chat_history, ""  # Ignore empty messages

    # Get context description
    context_description = RAG_CONTEXTS.get(selected_context, "General Chatbot")

    # Generate bot response
    bot_reply = f"[{selected_context} Context] {context_description} - You asked: '{user_text}'"

    # Append user message first
    updated_history = list(chat_history)
    updated_history.append({"role": "user", "content": user_text})

    # ✅ Force non-empty bot response (prevents flickering)
    if not bot_reply.strip():
        bot_reply = " "

    # Append bot message (ensures there's always content)
    updated_history.append({"role": "assistant", "content": bot_reply})

    return updated_history, ""  # ✅ Ensures no flickering



# -------------------------------------------
# Start a new chat, optionally save old one
# -------------------------------------------
def start_new_chat(selected_context, chat_history, session_list):
    print("[DEBUG] start_new_chat() triggered with context=", selected_context)
    
    if chat_history:
        # Save previous session if not empty
        chat_name = generate_chat_name()
        chat_sessions[chat_name] = list(chat_history)
        session_list = list(session_list)
        session_list.append(chat_name)

        print("[DEBUG] Saved session as:", chat_name, "with", len(chat_history), "messages")

    welcome_message = f"🔄 New chat started with **{selected_context}** context!"
    
    # Update session HTML
    session_html = create_session_html(session_list)
    
    # Fresh chat: assistant greeting
    new_chat = [{"role": "assistant", "content": welcome_message}]
    
    # Return new chat, cleared chat_history, updated session_list, updated HTML
    return new_chat, [], session_list, session_html

# ---------------------------------------------
# Load a past chat by index from 'session_list'
# ---------------------------------------------
def load_chat(selected_index_str, session_list):
    print("[DEBUG] load_chat() triggered with selected_index_str=", selected_index_str)
    
    try:
        idx = int(selected_index_str)
        if 0 <= idx < len(session_list):
            chat_name = session_list[idx]
            print("[DEBUG] Loading chat_name =", chat_name)
            if chat_name in chat_sessions:
                return chat_sessions[chat_name]
    except (ValueError, TypeError):
        print("[DEBUG] Invalid index or parse error.")
    
    return []  # Return empty if invalid selection

# ---------------------------------------------
# Build HTML for sessions (sidebar list)
# ---------------------------------------------
def create_session_html(sessions):
    print("[DEBUG] create_session_html() with sessions=", sessions)
    
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
    
    # Minimal inline CSS for styling
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
# JavaScript snippet in <head>, using <script> tags
# NOTE: We dispatch an 'input' event, and we look for '#session-select-callback textarea'
# because Gradio encloses the <textarea> in a container with id='session-select-callback'
# ----------------------------------------------
custom_js = """
<script>
document.addEventListener("click", function(e){
  var item = e.target.closest(".session-item");
  if (!item) return;

  console.log("[DEBUG] Clicked .session-item with index:", item.dataset.index);

  // We select the actual <textarea> inside #session-select-callback
  var hiddenBox = document.querySelector("#session-select-callback textarea");
  if (hiddenBox) {
    hiddenBox.value = item.dataset.index;
    console.log("[DEBUG] Setting hidden callback value:", hiddenBox.value);
    // Dispatch 'input' event to match .input(...) in Python
    hiddenBox.dispatchEvent(new Event("input", { bubbles: true }));
  } else {
    console.log("[DEBUG] #session-select-callback textarea not found!");
  }
});
</script>
"""

# =============================================
#    Gradio UI Setup with Blocks
# =============================================
with gr.Blocks(
    head=custom_js,
    theme=gr.themes.Base(primary_hue="blue", neutral_hue="gray", text_size=gr.themes.sizes.text_md),
    css="""

/* === Ensure No Hidden Width Expansion Anywhere === */
* {
    max-width: 100vw !important;
}

/* === Ensure Full-Screen View Without Overflow === */
html, body {
    width: 100vw;
    height: 100vh;
    max-width: 100vw;
    max-height: 100vh;
    background-color: #0f172a;
    color: #f0f0f0;
    overflow-x: hidden !important; /* Prevents overflow */
    display: flex;
    justify-content: flex-start; /* Ensures everything starts from left */
}

/* === Fix .wrap to Prevent Right Overflow While Adding Space === */
.wrap.svelte-1byz9vf {
    flex-grow: 1;
    width: 100vw !important; /* Ensures it takes the full width */
    max-width: 100vw !important;
    display: flex !important;
    justify-content: flex-start !important;
    align-items: stretch !important;
    padding-right: 15px !important; /* FIX: Adds right space without overflow */
    margin: 0 !important;
    overflow-x: hidden !important;
}

/* === Ensure Parent Container Fully Expands But Doesn't Overflow === */
.contain.svelte-1byz9vf {
    display: flex !important;
    flex-grow: 1 !important;
    width: 100vw !important;
    max-width: 100vw !important;
    justify-content: flex-start !important;
    align-items: stretch !important;
    overflow-x: hidden !important;
    padding-right: 50px !important; /* FIX: Adds right padding */
    margin: 0 !important;
}

/* === Ensure Main Row Uses Full Width Without Overflow === */
#main-row {
    display: flex !important;
    flex-grow: 1 !important;
    width: 100vw !important; /* FIX: Ensures right space but no overflow */
    max-width: 100vw !important;
    padding: 0px;
    gap: 0px;
    overflow-x: hidden !important;
    padding-right: 15px !important; /* FIX: Right space without causing overflow */
}

/* === Sidebar (No Changes, Just Ensuring Proper Width) === */
.sidebar {
    flex: 0 0 220px;
    height: 100%;
    background-color: #1e293b;
    padding: 20px;
    border-right: 2px solid #334155;
    display: flex;
    flex-direction: column;
    align-items: center;
}

/* === Ensure Main Column Fills Remaining Space Properly with Padding Instead of Margin === */
.main-column {
    flex-grow: 1;
    width: calc(100vw - 220px) !important; /* FIX: Ensure no overflow */
    max-width: calc(100vw - 220px) !important;
    padding-right: 15px !important; /* FIX: Adds right spacing without overflow */
    border-radius: 10px;
    background-color: #1e293b;
    overflow-x: hidden;
}

/* === Fix Chatbot Container to Prevent Overflow While Allowing Right Space === */
#component-11 {
    width: 100% !important;
    max-width: 100% !important;
    min-width: 100% !important;
    min-height: 100%;
    border-radius: 12px;
    background-color: #0f172a;
    padding-right: 15px !important; /* FIX: Adds right spacing */
    border: 1px solid #334155;
    box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.3);
    overflow-x: hidden;
}

/* === FINAL FIX: Force App to Stay Within Screen But Allow Right Padding === */
#component-0.column.svelte-vt1mxs {
    width: 100% !important; /* FIX: Ensures correct width */
    max-width: 100vw !important;
    flex-grow: 1 !important;
    overflow-x: hidden !important;
    padding-right: 15px !important; /* FIX: Adds right spacing */
}
/* === Fix Avatar Size Flickering === */
.chatbot .chat-message.bot img {
    width: 40px !important;  /* Adjust based on your avatar */
    height: 40px !important;
    object-fit: contain;
    border-radius: 50%;
}
.chatbot .chat-message.bot img {
    width: 40px !important;  /* Ensures fixed avatar size */
    height: 40px !important;
    object-fit: contain;
    border-radius: 50%;
}

/* === Prevent Empty Chat Messages from Enlarging Avatar === */
.chatbot .chat-message.bot:empty::after {
    content: " ";  /* Prevents Gradio from treating empty messages as missing */
    display: inline-block;
    visibility: hidden;
}

"""
) as demo:
    with gr.Row(min_height=700):
        # -------------- Sidebar --------------
        with gr.Column(scale=1, elem_classes=["sidebar"], min_width=250):
            gr.Markdown("## 📁 Chat History")

            new_chat_btn = gr.Button("➕ New Chat", elem_classes=["new-chat-btn"])
            session_list = gr.State([])  
            session_html = gr.HTML("<div class='session-list'>No saved chats yet</div>")
            
            # Hidden textbox for session selection
            # Must have interactive=True + the correct elem_id
            session_select_callback = gr.Textbox(
                elem_id="session-select-callback", 
                visible=False,
                interactive=True
            )

        # -------------- Main Chat UI --------------
        with gr.Column(min_width=1100,scale=30):
            gr.Markdown("# 🤖 Chatbot with RAG Embedding Context")

            context_selector = gr.Dropdown(
                choices=list(RAG_CONTEXTS.keys()),
                value="Science",
                label="Select Embedding Context"
            )

            chatbot = gr.Chatbot(
                label="Chatbot",
                type="messages",
                avatar_images=["DRP.png", "USR.png"],
                min_height=650,
                min_width=900,
                height=650,  # Ensures it doesn’t dynamically resize
            )

            with gr.Row():
                message_input = gr.MultimodalTextbox(
                    show_label=False, 
                    placeholder="Type your message here...",
                    file_types=[".pdf", ".txt"],
                    scale=10,
                )
                send_btn = gr.Button("Send", scale=2)

            chat_history = gr.State([])

            # --- Send message handler ---
            def handle_message(user_input, history, context):
                print("[DEBUG] handle_message triggered.")
                new_history, _ = chatbot_response(user_input, history, context)
                return new_history, ""

            # -- Send button click
            send_btn.click(
                handle_message,
                inputs=[message_input, chat_history, context_selector],
                outputs=[chatbot, message_input]
            ).then(
                lambda x: x,
                inputs=[chatbot],
                outputs=[chat_history]
            )

            # -- Pressing Enter in the message_input
            message_input.submit(
                handle_message,
                inputs=[message_input, chat_history, context_selector],
                outputs=[chatbot, message_input]
            ).then(
                lambda x: x,
                inputs=[chatbot],
                outputs=[chat_history]
            )

            # -- Changing context => new chat
            context_selector.change(
                start_new_chat,
                inputs=[context_selector, chat_history, session_list],
                outputs=[chatbot, chat_history, session_list, session_html]
            )

            # -- "New Chat" button
            new_chat_btn.click(
                start_new_chat,
                inputs=[context_selector, chat_history, session_list],
                outputs=[chatbot, chat_history, session_list, session_html]
            )

            # -- Loading a past session
            #   session_select_callback is triggered by JS dispatchEvent("input")
            session_select_callback.input(
                load_chat,
                inputs=[session_select_callback, session_list],
                outputs=[chatbot]
            ).then(
                lambda x: x,
                inputs=[chatbot],
                outputs=[chat_history]
            )

            # -- On initial load, show a welcome
            demo.load(
                lambda: [{"role": "assistant", "content": "👋 Welcome! This chatbot uses the **Science** context."}],
                outputs=[chatbot]
            ).then(
                lambda x: x,
                inputs=[chatbot],
                outputs=[chat_history]
            )

demo.launch()
