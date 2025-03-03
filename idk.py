import gradio as gr
import datetime
import chromadb
from sentence_transformers import SentenceTransformer
import base64
#== Work from here============
# === Simulated RAG Embedding Contexts ===
RAG_CONTEXTS = {
    "Science": "This chatbot specializes in answering science-related questions.",
    "History": "This chatbot provides insights into historical events and figures.",
    "Technology": "This chatbot discusses the latest advancements in technology.",
}

with open("W3_Nobg.png", "rb") as img_file:
    base64_str = base64.b64encode(img_file.read()).decode()

markdown_content = f"""
<h1 style="display: flex; align-items: center; gap: 10px;">
    <img src="data:image/png;base64,{base64_str}" width="40"/>W3 BrainBot
</h1>
"""

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

footer {
    display: none !important;
    visibility: hidden !important;
    position: absolute !important;
    height: 0 !important;
    width: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
}

/* === Ensure Full-Screen View Without Overflow === */
html, body {
    width: 100vw;
    height: 100vh;
    max-width: 100vw;
    max-height: 100vh;
    background-color: #090f1c;
    color: #090f1c;
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
    padding-right: 0px !important; /* FIX: Adds right space without overflow */
    margin: 0 !important;
    overflow-x: hidden !important;
    background-color: #090f1c;
    margin-left: 0px;
}

.fillable.svelte-69rnjb{
    margin-left: 0px !important;
    padding: 0px !important;
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
    padding-right: 0px !important; /* FIX: Adds right padding */
    margin: 0 !important;
    background-color: #090f1c;
    padding-bottom: 0px !important;
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
    background-color: #090f1c;
}

/* === Sidebar (No Changes, Just Ensuring Proper Width) === */
.sidebar {
    flex: 0 0 220px;
    height: 100%;
    background-color: #090f1c;
    padding: 20px;
    border-right: 3px solid #1e2d4f;
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
    background-color: #090f1c;
    overflow-x: hidden;
}

/* === Fix Chatbot Container to Prevent Overflow While Allowing Right Space === */
#component-11 {
    width: 100% !important;
    max-width: 100% !important;
    min-width: 100% !important;
    min-height: 100%;
    border: 1px solid #090f1c;
    background-color: #090f1c;
    padding-right: 300px !important; /* FIX: Adds right spacing */
    padding-left: 300px !important; /* FIX: Adds left spacing */
    overflow-x: hidden;
}

/* === FINAL FIX: Force App to Stay Within Screen But Allow Right Padding === */
#component-0.column.svelte-vt1mxs {
    width: 100% !important;
    max-width: 100vw !important;
    flex-grow: 1 !important;  /* Ensures it fills available space */
    flex-shrink: 0 !important;
    overflow-x: hidden !important;
    padding: 0px !important; /* Remove any unnecessary padding */
    margin: 0px !important;  /* Remove extra margins */
    height: 100vh !important; /* Set to full viewport height */
    min-height: 100vh !important; /* Ensure it stretches */
    display: flex !important;
    flex-direction: column !important;
}


#component-1{
    padding-top: 0px;
    margin-top: 0px;
}

.html-container.svelte-phx28p.padding{
    padding: 0px;
}

#component-9{
    border: 0px;
    margin-right:20px;
}

.svelte-633qhp{
    margin-top: 0px !important;
    background-color: #090f1c !important;
    display: flex !important;
    justify-content: flex-start !important; /* Align items to the left */
    align-items: center !important;
    width: 210px;
    height: 80px;
    padding: 0px;
    border: 1px solid #090f1c;
}

/*================================Selector De Context================================*/
/* === Make Context Selector Shorter & Blend In === */
#context-selector {
    width: 200px !important; /* Adjust width to your preference */
    min-width: 200px !important;
    max-width: 200px !important;
    background-color: #090f1c !important; /* Hide background */
    color: #ffffff !important; /* Ensure text is visible */
    padding: 0px !important; /* Adjust padding */
    align-items: left !important;
    height: 50px !important;
}

/* === Hide Inner Background but Keep Text & Border === */
#context-selector .svelte-1hfxrpf.container {
    background-color: #090f1c !important;
}

/* === Style the Input Box Inside Selector === */
#context-selector input {
    background-color: #090f1c !important; /* Transparent background */
    color: #ffffff !important; /* Text color */
    height: 40px !important; /* Adjust height */
    font-size: 18px !important; /* Adjust text size */
}

/* === Style the Dropdown Arrow to Blend In === */
#context-selector .icon-wrap svg {
    fill: #ffffff !important; /* Change arrow color */
    opacity: 0.7 !important; /* Slight transparency */
}

/* === Ensure Proper Layout === */
#context-selector .wrap {
    justify-content: center !important;
    align-items: center !important;
    padding: 0 !important;
}

/* === Remove Any Extra Margins/Padding === */
#context-selector .wrap,
#context-selector .wrap-inner,
#context-selector .secondary-wrap {
    margin: 0 !important;
    padding: 0 !important;
}

/*=====================================Fin===========================================*/

#component-12{
    border: 0px !important;
    background-color: #090f1c !important;
    padding: 0px 350px !important;
}

.wrapper.svelte-g3p8na {
    background-color: #090f1c !important;
    border-color: #090f1c !important;
}

/* Change chat area background */
.bubble-wrap.svelte-gjtrl6 {
    background-color: #090f1c !important;
    border-color: #090f1c; !important
}
#message-input{
    height: 100%;
    border-radius: 12px;
    border: 2px solid red;
}
.svelte-d47mdf{
    padding: 10px 5px;
}
/* Change chatbot message background */
"""
) as demo:
    with gr.Row(min_height=700):
        # -------------- Sidebar --------------
        with gr.Column(scale=1, elem_classes=["sidebar"], min_width=250):
            gr.Markdown(markdown_content)

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
        with gr.Column(min_width=1100,scale=30, elem_classes=["main-chat-ui"]):

            context_selector = gr.Dropdown(
                choices=list(RAG_CONTEXTS.keys()),
                value="Science",
                show_label=False,
                elem_id="context-selector",
            )

            chatbot = gr.Chatbot(
                show_label=False,
                type="messages",
                min_height=750,
                min_width=600,
                height=650,  # Ensures it doesn’t dynamically resize
            )

            with gr.Row():
                message_input = gr.MultimodalTextbox(
                    show_label=False, 
                    placeholder="Type your message here...",
                    file_types=[".pdf", ".txt", ".png", ".jpg", ".jpeg"],
                    scale=10,
                    elem_id="message-input",
                )

            chat_history = gr.State([])

            # --- Send message handler ---
            def handle_message(user_input, history, context):
                print("[DEBUG] handle_message triggered.")
                new_history, _ = chatbot_response(user_input, history, context)
                return new_history, ""

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

demo.launch(favicon_path='W3_Nobg.png', server_name="192.168.0.227", server_port=8000)
