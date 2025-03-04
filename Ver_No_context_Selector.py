import gradio as gr
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

    return updated_history, bot_reply  # Return updated history and bot reply

# -------------------------------------------
# Start a new chat, optionally save old one
# -------------------------------------------
def start_new_chat(chat_history, session_list):
    print("[DEBUG] start_new_chat() triggered")

    if chat_history:
        # Save previous session if not empty
        chat_name = session_list[0]  # Get the first session (since New Chat is on top)
        chat_sessions[chat_name] = list(chat_history)
        print("[DEBUG] Saved session as:", chat_name, "with", len(chat_history), "messages")

    # ✅ Remove existing "New Chat" if it exists
    if "New Chat" in session_list:
        session_list.remove("New Chat")

    # ✅ Always insert a new "New Chat" at the top
    chat_name = "New Chat"
    session_list.insert(0, chat_name)
    chat_sessions[chat_name] = [{"role": "assistant", "content": "🔄 New chat started!"}]

    print(f"[DEBUG] Created new session at the top: {chat_name}")

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

    # If no sessions, just return an empty container
    if not sessions:
        return "<div class='session-list'></div>"

    # Open the main session-list container once
    html = "<div class='session-list'>"
    for i, session in enumerate(sessions):
        # Skip "New Chat" so it doesn't show until renamed
        if session == "New Chat":
            continue

        html += f"""
        <div class="session-item" data-index="{i}">
            <div class="session-name">{session}</div>
            <div class="options" data-session-id="{i}">⁝</div>
        </div>
        """
    # Close out the session-list container
    html += "</div>"

    # Single (global) modal element (not nested in each item)
    html += """
    <div id="modal" class="modal">
        <div class="modal-content">
            <button class="rename-btn">Rename</button>
            <button class="delete-btn">Delete</button>
        </div>
    </div>
    """

    # Minimal inline CSS for styling
    html += """
    <style>
/* Sidebar containing session list */
/* Ensure the main container is a flexbox with 100% height */
.main-container {
    display: flex;
    height: 100vh;  /* Ensure full screen height */
    width: 100%;    /* Ensure full width */
}

/* Sidebar settings */
.sidebar {
    display: flex;  /* Maintain flexbox behavior */
    flex-direction: column;  /* Stack children vertically */
    flex: 0 0 220px;   /* Fixed width for the sidebar */
    height: 100vh;     /* Ensure sidebar fills the screen height */
    background-color: #090f1c;
    padding: 20px;
    border-right: 3px solid #1e2d4f;
    align-items: center;
    overflow-x: hidden; /* Prevent horizontal overflow */
    overflow-y: auto;   /* Allow vertical scrolling */
    box-sizing: border-box;
}

/* Session list container with scrolling enabled */
.session-list {
    display: flex;
    flex-direction: column; /* Stack session items vertically */
    gap: 0px;
    width: 100%;  /* Ensure the width is 100% */
    margin-top: 10px;
    color: #f0f0f0;
    text-align: left; /* Allow the list to grow but not exceed the sidebar height */
    overflow-y: auto; /* Enable vertical scrolling */
    max-height: calc(100vh - 40px);  /* Set max height, considering padding */
    padding-right: 5px;  /* Optional padding to make it visually cleaner */
}

/* Session item styling */
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
    margin-top: -2px;
    position: relative;
    flex-shrink: 0;  /* Prevent shrinking, so items maintain their size */
}

/* Options button inside each session */
.options {
    margin: 0px;
    width: 5%;
    text-align: center;
    font-size: 18px;
    font-weight: 600;
    padding-top: 2px;
    border-radius: 20px;
    transition: border 0.3s;
    display: none; /* Hide by default */
    transition: opacity 0.3s ease-in-out;
}

/* Show options button on hover */
.session-item:hover .options {
    display: block; /* Show on hover */
}

/* Hover effects for session item */
.options:hover {
    font-weight: 800;
}

.session-item:hover {
    background-color: #4a4a4a;
}

/* Session name in each item */
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
    </style>
    """

    return html

# =============================================
#    Gradio UI Setup with Blocks
# =============================================

def handle_message(user_input, history, session_list):
    print("[DEBUG] handle_message triggered with:", user_input)

    # Convert Gradio state to a mutable list
    session_list = list(session_list)

    # Extract user text from user_input (could be dict if a file was uploaded)
    user_text = ""
    if isinstance(user_input, dict):
        user_text = user_input.get("text", "").strip()
    else:
        user_text = str(user_input).strip()

    # If user typed nothing, return early
    if not user_text:
        # define session_html so it won't be undefined
        session_html = create_session_html(session_list)
        print("[DEBUG] Empty user input. Returning.")
        return history, "", session_list, session_html

    # Ensure session_list has at least one session
    if not session_list:
        session_list.insert(0, "New Chat")
        chat_sessions["New Chat"] = [{"role": "assistant", "content": "🔄 New chat started!"}]
        print("[DEBUG] Initialized session list with 'New Chat'")

    # The latest session name
    chat_name = session_list[0]

    # If it's still "New Chat", rename it to first 20 chars of user_text
    if chat_name == "New Chat":
        new_name = user_text[:20] + "..."  # up to 20 chars + "..."
        session_list[0] = new_name
        if "New Chat" in chat_sessions:
            chat_sessions[new_name] = chat_sessions.pop("New Chat")
        else:
            chat_sessions[new_name] = []
        chat_name = new_name
        print(f"[DEBUG] Renamed 'New Chat' to: {chat_name}")

    # Process user input with chatbot_response
    new_history, _ = chatbot_response(user_text, history)

    # Save updated history
    chat_sessions[chat_name] = new_history

    # Always define session_html before returning
    session_html = create_session_html(session_list)

    return new_history, "", session_list, session_html

custom_js = """
<script>
document.addEventListener("click", function(e) {
  var item = e.target.closest(".session-item");
  var optionsBtn = e.target.closest(".options");
  var modal = document.getElementById('modal');

  // Handle session item click to load chat
  if (item && !optionsBtn) {
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
  }

  // Handle options button click to toggle modal visibility
  if (optionsBtn) {
    console.log("[DEBUG] Options button clicked for session ID:", optionsBtn.dataset.sessionId);

    if (!modal) {
      console.error("[ERROR] Modal with id 'modal' not found!");
      return;
    }

    // Toggle visibility of the modal
    if (modal.style.display === "none" || modal.style.display === "") {
      console.log("[DEBUG] Showing modal");
      modal.style.display = "block";  // Show the modal
      var rect = optionsBtn.getBoundingClientRect();
      console.log("[DEBUG] Positioning modal at top:", rect.bottom + window.scrollY, "left:", rect.left);
      // Position the modal just below the options div
      modal.style.top = (rect.bottom + window.scrollY + 50) + "px";
      modal.style.left = (rect.left + 40) + "px";  // Align the modal with the options div
    }
  } 
  // Close the modal if it's open and clicked anywhere else
  else if (modal && modal.style.display === "block") {
    console.log("[DEBUG] Clicking outside of options button, closing modal.");
    modal.style.display = "none";  // Close the modal
  }

  // Handle rename button click
  if (e.target.classList.contains('rename-btn')) {
    var sessionId = optionsBtn ? optionsBtn.dataset.sessionId : null;
    console.log("[DEBUG] Rename button clicked for session ID:", sessionId);
    var newName = prompt("Enter new session name:");
    if (newName) {
      console.log("[DEBUG] Renaming session:", newName);

      // Rename the session in the backend (Python) logic here
      // (Currently not implemented in this snippet)

      modal.style.display = "none"; // Close modal after renaming
    }
  }

  // Handle delete button click
  if (e.target.classList.contains('delete-btn')) {
    var sessionId = optionsBtn ? optionsBtn.dataset.sessionId : null;
    console.log("[DEBUG] Delete button clicked for session ID:", sessionId);
    if (confirm("Are you sure you want to delete this session?")) {
      console.log("[DEBUG] Deleting session with ID:", sessionId);
      // Implement the delete logic here
      modal.style.display = "none"; // Close modal after deleting
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

.fillable.svelte-vnblmh.app{
    margin: 0px;
    padding: 0px;
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
    height: 100vh;
    display: block;
}

#component-3{
    margin-bottom: 10px;
}

#component-4{
    font-size: 14px;
    font-weight: 600;
    justify-content: flex-start;
    display: flex;
    padding: 10px;
    
}
#component-6{
    display: block;
    overflow-y: auto;
    overflow-x: hidden;
}

/* === Ensure Main Column Fills Remaining Space Properly with Padding Instead of Margin === */
.main-column {
    flex-grow: 1;
    width: calc(100vw - 220px) !important; /* FIX: Ensure no overflow */
    max-width: calc(100vw - 220px) !important;
    padding-right: 15px !important; /* FIX: Adds right spacing without overflow */
    background-color: #090f1c;
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
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


demo.launch(favicon_path='W3_Nobg.png', server_name="192.168.0.35", server_port=8000)
