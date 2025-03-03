import gradio as gr
import datetime
from sentence_transformers import SentenceTransformer
import base64
import time

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
    return "New Chat"  # ✅ Always start with "New Chat"


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
        chat_name = session_list[-1]
        chat_sessions[chat_name] = list(chat_history)

        print("[DEBUG] Saved session as:", chat_name, "with", len(chat_history), "messages")

    # ✅ Reset chat & create "New Chat" session
    chat_name = "New Chat"
    session_list.append(chat_name)
    chat_sessions[chat_name] = [{"role": "assistant", "content": "🔄 New chat started!"}]

    print(f"[DEBUG] Created new session: {chat_name}")

    # ✅ Update session list UI
    session_html = create_session_html(session_list)

    return [{"role": "assistant", "content": "🔄 New chat started!"}], [], session_list, session_html

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
        <div class="session-list">
            <div class="session-item" data-index="0">
                <div class="session-name">{session}</div>
                <div class="options" data-session-id={i}>⁝</div>
            </div>
            <!-- No modal here anymore -->
        </div>

        <!-- Independent modal that is outside of session items -->
        <div id="modal" class="modal">
            <div class="modal-content">
                <button class="rename-btn">Rename</button>
                <button class="delete-btn">Delete</button>
            </div>
        </div>      
        """
    html += "</div>"
    
    # Minimal inline CSS for styling
    html += """
    <style>

.session-list {
    display: flex;
    flex-direction: column;
    gap: 0px;
    width: 100%;
    margin-top: 10px;
    color: #f0f0f0;
    text-align: left;
}

.session-item {
    display: flex;
    justify-content: space-between;
    padding: 10px;
    border-radius: 5px;
    background-color: #090f1c;
    cursor: pointer;
    transition: background-color 0.3s;
    color: #f0f0f0;
    border: 1px solid #090f1c;
    margin-top: -3px;
}

.options {
    margin: 0px;
    width: 5%;
    text-align: center;
    font-size: 18px;
    font-weight: 600;
    padding-top: 2px;
    border-radius: 20px;
    transition: border 0.3s;
}

.options:hover {
    font-weight: 800;
}

.session-item:hover {
    background-color: #4a4a4a;
}

.session-name {
    font-size: 14px;
    white-space: nowrap;
    overflow: hidden;
    margin-top: 5px;
    text-overflow: ellipsis;
    margin-left: 8px;
    width: 80%;
}

/* Modal Styles */
.modal {
    display: none; /* Hide the modal by default */
    position: fixed; /* Position it fixed at the topmost level */
    top: 0px;
    left: 0px;
    transform: translate(-50%, -50%); /* Center it on the screen */
    background-color: #333;
    border-radius: 5px;
    padding: 20px;
    color: #fff;
    z-index: 9999; /* Ensure it is on top */
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
}

.modal-content {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.rename-btn, .delete-btn {
    margin: 5px 0;
    padding: 8px;
    border-radius: 5px;
    background-color: #5e5e5e;
    color: white;
    border: none;
    cursor: pointer;
}

.rename-btn:hover, .delete-btn:hover {
    background-color: #4c4c4c;
}

    """
    return html

# ----------------------------------------------
# JavaScript snippet in <head>, using <script> tags
# ----------------------------------------------
custom_js = """
<script>
document.addEventListener("click", function(e) {
  var item = e.target.closest(".session-item");
  var optionsBtn = e.target.closest(".options");
  var modal = document.getElementById('modal');

  // Handle session item click to load chat
  if (item && !optionsBtn) {
    console.log("[DEBUG] Clicked .session-item with index:", item.dataset.index);

    var hiddenBox = document.querySelector("#session-select-callback textarea");
    if (hiddenBox) {
      hiddenBox.value = item.dataset.index;
      console.log("[DEBUG] Setting hidden callback value:", hiddenBox.value);
      hiddenBox.dispatchEvent(new Event("input", { bubbles: true }));
    } else {
      console.log("[DEBUG] #session-select-callback textarea not found!");
    }
  }

  // Handle options button click to show modal
  if (optionsBtn) {
    console.log("[DEBUG] Options button clicked for session ID:", optionsBtn.dataset.sessionId);
    
    if (!modal) {
      console.error("[ERROR] Modal with id 'modal' not found!");
      return;
    }

    // Store selected session ID
    window.selectedSessionId = optionsBtn.dataset.sessionId;

    // Show modal
    modal.style.display = "block";
  } 
  else if (modal && modal.style.display === "block") {
    modal.style.display = "none";  // Close modal if clicking outside
  }
});

// Handle rename button click
document.querySelector(".rename-btn").addEventListener("click", function() {
  if (window.selectedSessionId !== undefined) {
    var newName = prompt("Enter new session name:");
    if (newName) {
      console.log("[DEBUG] Renaming session:", newName);

      var renameBox = document.querySelector("#session-rename-callback textarea");
      if (renameBox) {
        renameBox.value = window.selectedSessionId + "||" + newName;
        renameBox.dispatchEvent(new Event("input", { bubbles: true }));
      }
    }
  }
});

// Handle delete button click
document.querySelector(".delete-btn").addEventListener("click", function() {
  if (window.selectedSessionId !== undefined) {
    if (confirm("Are you sure you want to delete this session?")) {
      console.log("[DEBUG] Deleting session ID:", window.selectedSessionId);

      var deleteBox = document.querySelector("#session-delete-callback textarea");
      if (deleteBox) {
        deleteBox.value = window.selectedSessionId;
        deleteBox.dispatchEvent(new Event("input", { bubbles: true }));
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

#component-2{
    height: 100%;
}

#component-3{
    margin-bottom: 10px;
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

#component-4{
    font-size: 14px;
    font-weight: 600;
    justify-content: flex-start;
    display: flex;
    padding: 10px;
    
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
    padding-right: 320px !important; /* FIX: Adds right spacing */
    padding-left: 300px !important; /* FIX: Adds left spacing */
    overflow-x: hidden;
    margin-bottom: 0px !important;
    padding-bottom: 0px !important;
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
    height: 100%;
}

.html-container.svelte-phx28p.padding{
    padding: 0px;
}

#component-9{
    padding-top: 30px;
    border: 0px;
    margin-right:0px;
}

#component-10{
    border: 1px solid #090f1c;
    margin-bottom: 0px !important;
    padding-bottom: 0px !important;
}

.svelte-633qhp{
    margin-top: 0px !important;
    background-color: #090f1c !important;
    display: flex !important;
    justify-content: flex-start !important; /* Align items to the left */
    align-items: center !important;
    width: 210px;
    height: 100px;
    padding: 0px;
    border: 1px solid #888888;
    border-radius: 50px;
}

.form.svelte-633qhp.hidden{
    border: 1px solid #090f1c;
}

.bot.svelte-pcjl1g.message{
    border-radius: 25px 5px 25px 5px;
    padding: 5px 14px 5px 14px;
    border: 1px solid #888888;
}

.user.svelte-pcjl1g.message{
    border-radius: 5px 25px 5px 25px;
    padding: 5px 14px 5px 14px;
    border: 1px solid #888888;
}

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
    border: 2px solid white;
}
.svelte-d47mdf{
    padding: 10px 5px;
}

.upload-button.svelte-d47mdf {
    position: absolute;
    display: none;
    visibility: hidden !important;
    width: 0 !important;
    height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    opacity: 0 !important;
    pointer-events: none !important;
}


.textbox {
    margin-left: 10px;
    margin-right: 10px;
    font-size: 18px; /* Increased from 15px */
    margin: -10px;
}

.full-container.svelte-d47mdf {
    max-height: 100%; /* Ensure it doesn't grow beyond parent */
    overflow: hidden; /* Hide overflow */
    display: flex;
    flex-direction: column;
    
    margin-top: 5px;
    position: relative; /* For absolute positioning of children */
}

.scroll-hide.svelte-d47mdf.no-label {
    margin-left: 55px;
    margin-right: 80px; /* Increased right margin to make room for the button */
    max-height: 200px; /* Set a reasonable max height */
    overflow-y: auto; /* Allow scrolling within textarea if content is long */
    resize: none; /* Prevent manual resizing which can break layout */
    font-size: 18px; /* Increased font size from 15px */
    line-height: 1.5; /* Better readability with increased line height */
    background-color: #090f1c !important;
}

.submit-button{
    margin-bottom: 8px;
    margin-right: 50px;
}

.submit-button.svelte-d47mdf {
    position: absolute;
    right: 50px;
    top: 12px; /* Adjusted to match the textbox's position */
    margin: 0;
    z-index: 2; /* Ensure button stays on top */
    width: 45px !important; /* Increased from default */
    height: 45px !important; /* Increased from default */
    padding: 8px !important; /* Adjust padding for better SVG placement */
    border-radius: 50%; /* Make it perfectly round */
    display: flex;
    align-items: center;
    justify-content: center;
}

.submit-button.svelte-d47mdf svg {
    width: 100% !important;
    height: 100% !important;
    transform: scale(1.3); /* Scale up the SVG slightly */
}

.input-container.svelte-d47mdf {
    height: auto;
    max-height: 100%;
    display: flex;
    align-items: flex-start; /* Align items at the top */
    position: relative; /* For absolute positioning of children */
}

.message-wrap.svelte-gjtrl6{
    margin-right: 300px;
    margin-left: 290px;
}

.column.main-chat-ui.gap {
  gap: 0; /* Remove any gap between child elements */
}
#component-10.block {
  margin-bottom: 0;
}
#component-11.row {
  margin-top: -10px; /* Adjust this value as needed */
}
.spaced-icon-btn::first-letter {
    margin-right: 10px;
}

.block.multimodal-textbox.svelte-11xb1hd{
    background-color: #090f1c;
}
.icon-button-wrapper.top-panel.hide-top-corner.svelte-1jx2rq3{
    display: none;
}
/* Change chatbot message background */
"""
) as demo:
    with gr.Row(min_height=700):
        # -------------- Sidebar --------------
        with gr.Column(scale=1, elem_classes=["sidebar"], min_width=250):
            gr.Markdown(markdown_content)

            new_chat_btn = gr.Button("➕  New Chat", elem_classes=["new-chat-btn", "spaced-icon-btn"], interactive=False)
            session_list = gr.State([])  
            session_html = gr.HTML("<div class='session-list'></div>")
            
            # Hidden textbox for session selection
            # Must have interactive=True + the correct elem_id
            session_select_callback = gr.Textbox(
                elem_id="session-select-callback", 
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
            def handle_message(user_input, history, session_list):
                print("[DEBUG] handle_message triggered with:", user_input)

                # Ensure user_input is a string
                if isinstance(user_input, dict):  # If input is multimodal (e.g., file or text)
                    user_text = user_input.get("text", "").strip()
                else:
                    user_text = str(user_input).strip()

                if not user_text:
                    print("[DEBUG] Empty user input. Ignoring.")
                    return history, "", session_list, create_session_html(session_list)

                session_list = list(session_list)  # Convert Gradio state to a mutable list

                # ✅ Ensure "New Chat" exists in session_list
                if not session_list:
                    session_list.append("New Chat")
                    print("[DEBUG] Initialized session list with 'New Chat'")

                # ✅ Ensure "New Chat" exists in chat_sessions
                if "New Chat" not in chat_sessions:
                    chat_sessions["New Chat"] = [{"role": "assistant", "content": "🔄 New chat started!"}]
                    print("[DEBUG] Initialized 'New Chat' in chat_sessions")

                # ✅ Get the latest session (before renaming)
                chat_name = session_list[-1]

                # ✅ Rename "New Chat" dynamically based on first user message (ONLY ONCE)
                if chat_name == "New Chat":
                    new_name = user_text[:20] + "..."  # Limit to first 20 characters
                    session_list[-1] = new_name  # ✅ Update the session list with new name

                    # ✅ Move history safely
                    if "New Chat" in chat_sessions:  
                        chat_sessions[new_name] = chat_sessions.pop("New Chat")  # ✅ Safe .pop()
                    else:
                        chat_sessions[new_name] = []  # ✅ Prevent KeyError if missing

                    chat_name = new_name  # ✅ Update reference
                    print(f"[DEBUG] Renamed session to: {chat_name}")

                # ✅ Process chatbot response
                new_history, _ = chatbot_response(user_text, history)

                # ✅ Append the user's message correctly
                new_history.append({"role": "user", "content": user_text})

                # ✅ Save chat history under the correct session
                chat_sessions[chat_name] = new_history

                # ✅ Update session HTML dynamically
                session_html = create_session_html(session_list)

                return new_history, "", session_list, session_html  # ✅ Return updated chat history and session HTML

            message_input.submit(
                handle_message,
                inputs=[message_input, chat_history, session_list],
                outputs=[chatbot, message_input, session_list, session_html]
            ).then(
                lambda: gr.update(interactive=True),  # ✅ Enable "New Chat" button
                outputs=[new_chat_btn]
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
            ).then(
                lambda: gr.update(interactive=False),  # ✅ Disable button after creating "New Chat"
                outputs=[new_chat_btn]
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
                lambda: ([{"role": "assistant", "content": "👋 Welcome to W3 BrainBot!"}], ["New Chat"], create_session_html(["New Chat"])),
                outputs=[chatbot, session_list, session_html]
            ).then(
                lambda: gr.update(interactive=False),  # ✅ Disable "New Chat" button at startup
                outputs=[new_chat_btn]
            )

demo.launch(favicon_path='W3_Nobg.png', server_name="192.168.0.227", server_port=8000)
# , server_name="192.168.0.227", server_port=8000