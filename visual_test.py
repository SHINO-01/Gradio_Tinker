import gradio as gr
import datetime
from sentence_transformers import SentenceTransformer
import base64

# === Work from here============
# Global storage for saved chat sessions
chat_sessions = {}

with open("W3_Nobg.png", "rb") as img_file:
    base64_str = base64.b64encode(img_file.read()).decode()

markdown_content = f"""
<h1 style="display: flex; align-items: center; gap: 10px;">
    <img src="data:image/png;base64,{base64_str}" width="40"/>W3 BrainBot
</h1>
"""

# Generate a unique chat session name
def generate_chat_name():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# -------------------------------
# Chatbot response function
# (handles multimodal input too)
# -------------------------------
def chatbot_response(user_input, chat_history):
    print("[DEBUG] chatbot_response() called with user_input=", user_input)

    if isinstance(user_input, dict):  # e.g., user uploaded a file
        user_text = user_input.get("text", "")
    else:
        user_text = user_input.strip()

    if not user_text:
        print("[DEBUG] Empty user input. Ignoring.")
        return chat_history, ""  # Ignore empty messages

    # Generate bot response
    bot_reply = f"You asked: '{user_text}'"

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
def start_new_chat(chat_history, session_list):
    print("[DEBUG] start_new_chat() triggered")
    
    if chat_history:
        # Save previous session if not empty
        chat_name = generate_chat_name()
        chat_sessions[chat_name] = list(chat_history)
        session_list = list(session_list)
        session_list.append(chat_name)

        print("[DEBUG] Saved session as:", chat_name, "with", len(chat_history), "messages")

    welcome_message = f"🔄 New chat started!"
    
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
        return "<div class='session-list'></div>"
    
    html = "<div class='session-list'>"
    for i, session in enumerate(sessions):
        html += f"""
        <div class='session-item' data-index='{i}'>
            <div class='session-name'>{session}</div>
            <button class='rename-btn' data-index='{i}'>Rename</button>
            <button class='delete-btn' data-index='{i}'>Delete</button>
        </div>
        """
    html += "</div>"
    
    # Minimal inline CSS for styling
    html += """
    <style>
        .rename-btn, .delete-btn {
            background-color: #4CAF50; /* Green button */
            color: white;
            border: none;
            padding: 5px 10px;
            cursor: pointer;
            margin-left: 5px;
        }

        .delete-btn {
            background-color: #f44336; /* Red button */
        }

        .rename-btn:hover, .delete-btn:hover {
            background-color: #ddd;
            color: black;
        }
    </style>
    """
    return html

# Handle renaming a session
def rename_session(new_name, session_index, session_list):
    print("[DEBUG] Renaming session at index:", session_index, "to", new_name)
    if 0 <= session_index < len(session_list):
        session_list[session_index] = new_name
        return create_session_html(session_list)
    return None

# Handle deleting a session
def delete_session(session_index, session_list):
    print("[DEBUG] Deleting session at index:", session_index)
    if 0 <= session_index < len(session_list):
        del session_list[session_index]
        return create_session_html(session_list)
    return None

# ----------------------------------------------
# JavaScript snippet for handling button clicks
# ----------------------------------------------
custom_js = """
<script>
document.addEventListener("click", function(e){
  var item = e.target.closest(".session-item");
  if (!item) return;

  // Get session index
  var index = item.dataset.index;

  // Rename button click
  if (e.target.classList.contains("rename-btn")) {
    var newName = prompt("Enter new name for the session:");
    if (newName) {
      console.log("Renaming session to:", newName);
      // Call Gradio's rename session function
      var hiddenBox = document.querySelector("#rename-callback textarea");
      if (hiddenBox) {
        hiddenBox.value = newName + "|" + index; // Format: newName|index
        hiddenBox.dispatchEvent(new Event("input", { bubbles: true }));
      }
    }
  }

  // Delete button click
  if (e.target.classList.contains("delete-btn")) {
    if (confirm("Are you sure you want to delete this session?")) {
      console.log("Deleting session at index:", index);
      // Call Gradio's delete session function
      var hiddenBox = document.querySelector("#delete-callback textarea");
      if (hiddenBox) {
        hiddenBox.value = index; // Just the index for delete
        hiddenBox.dispatchEvent(new Event("input", { bubbles: true }));
      }
    }
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
    /* Add your existing CSS here */
    """
) as demo:
    with gr.Row(min_height=700):
        # -------------- Sidebar --------------
        with gr.Column(scale=1, elem_classes=["sidebar"], min_width=250):
            gr.Markdown(markdown_content)

            new_chat_btn = gr.Button("➕  New Chat", elem_classes=["new-chat-btn", "spaced-icon-btn"])
            session_list = gr.State([])  
            session_html = gr.HTML("<div class='session-list'></div>")
            
            # Hidden textbox for session selection
            session_select_callback = gr.Textbox(
                elem_id="session-select-callback", 
                visible=False,
                interactive=True
            )

            # Hidden textboxes for rename and delete operations
            rename_callback = gr.Textbox(
                elem_id="rename-callback", 
                visible=False, 
                interactive=True
            )
            delete_callback = gr.Textbox(
                elem_id="delete-callback", 
                visible=False, 
                interactive=True
            )

        # -------------- Main Chat UI --------------
        with gr.Column(min_width=1100,scale=30, elem_classes=["main-chat-ui"]):
            chatbot = gr.Chatbot(
                show_label=False,
                type="messages",
                min_height=790,
                min_width=600,
                height=650,  # Ensures it doesn't dynamically resize
                container=False,
                avatar_images=["USR_small.png","W3_Nobg_ssmall.png"],
                layout="bubble",
            )

            with gr.Row():
                message_input = gr.MultimodalTextbox(
                    show_label=False, 
                    placeholder="Type your message here...",
                    scale=10,
                    elem_id="message-input",
                    max_plain_text_length=8000,
                    max_lines=8000,
                )

            chat_history = gr.State([])

            # --- Send message handler ---
            def handle_message(user_input, history):
                print("[DEBUG] handle_message triggered.")
                new_history, _ = chatbot_response(user_input, history)
                return new_history, ""

            # -- Pressing Enter in the message_input
            message_input.submit(
                handle_message,
                inputs=[message_input, chat_history],
                outputs=[chatbot, message_input]
            ).then(
                lambda x: x,
                inputs=[chatbot],
                outputs=[chat_history]
            )

            # -- "New Chat" button
            new_chat_btn.click(
                start_new_chat,
                inputs=[chat_history, session_list],
                outputs=[chatbot, chat_history, session_list, session_html]
            )

            # -- Loading a past session
            session_select_callback.input(
                load_chat,
                inputs=[session_select_callback, session_list],
                outputs=[chatbot]
            ).then(
                lambda x: x,
                inputs=[chatbot],
                outputs=[chat_history]
            )

            # -- Rename session callback
            rename_callback.input(
                rename_session,
                inputs=[rename_callback, session_list],
                outputs=[session_html]
            )

            # -- Delete session callback
            delete_callback.input(
                delete_session,
                inputs=[delete_callback, session_list],
                outputs=[session_html]
            )

            # -- On initial load, show a welcome
            demo.load(
                lambda: [{"role": "assistant", "content": "👋 Welcome to W3 BrainBot!"}],
                outputs=[chatbot]
            ).then(
                lambda x: x,
                inputs=[chatbot],
                outputs=[chat_history]
            )

demo.launch(favicon_path='W3_Nobg.png', server_name="192.168.0.227", server_port=8000)
