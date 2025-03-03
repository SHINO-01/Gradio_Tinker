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

# ----------------------------------------------
# Delete a chat session
# ----------------------------------------------
def delete_chat(session_index_str, session_list):
    print("[DEBUG] delete_chat() triggered with session_index_str=", session_index_str)
    
    try:
        idx = int(session_index_str)
        if 0 <= idx < len(session_list):
            chat_name = session_list[idx]
            print("[DEBUG] Deleting chat_name =", chat_name)
            
            # Remove from storage
            if chat_name in chat_sessions:
                del chat_sessions[chat_name]
            
            # Remove from list
            new_session_list = list(session_list)
            new_session_list.pop(idx)
            
            # Update HTML
            session_html = create_session_html(new_session_list)
            
            return new_session_list, session_html
    except (ValueError, TypeError):
        print("[DEBUG] Invalid index or parse error.")
    
    return session_list, create_session_html(session_list)  # Return unchanged if error

# ----------------------------------------------
# Rename a chat session
# ----------------------------------------------
def rename_chat(data, session_list):
    print("[DEBUG] rename_chat() triggered with data=", data)
    
    try:
        # Parse data in format "index:new_name"
        idx_str, new_name = data.split(":", 1)
        idx = int(idx_str)
        
        if 0 <= idx < len(session_list):
            old_name = session_list[idx]
            print(f"[DEBUG] Renaming chat from '{old_name}' to '{new_name}'")
            
            # Update in storage by creating new entry and deleting old one
            if old_name in chat_sessions:
                chat_sessions[new_name] = chat_sessions[old_name]
                del chat_sessions[old_name]
            
            # Update in list
            new_session_list = list(session_list)
            new_session_list[idx] = new_name
            
            # Update HTML
            session_html = create_session_html(new_session_list)
            
            return new_session_list, session_html
    except (ValueError, TypeError, IndexError) as e:
        print("[DEBUG] Error in rename_chat:", e)
    
    return session_list, create_session_html(session_list)  # Return unchanged if error

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
            <div class='session-options-button' data-index='{i}'>⋮</div>
            <div class='options-menu' id='options-menu-{i}'>
                <div class='option rename-option' data-index='{i}'>Rename</div>
                <div class='option delete-option' data-index='{i}'>Delete</div>
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
        gap: 8px;
        width: 100%;
        margin-top: 10px;
        color: #f0f0f0;
        text-align: left;
    }
    .session-item {
        padding: 10px;
        border-radius: 5px;
        background-color: #3a3a3a;
        cursor: pointer;
        transition: background-color 0.3s;
        color: #f0f0f0;
        border: 1px solid #4f4f4f;
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: relative;
    }
    .session-item:hover {
        background-color: #4a4a4a;
    }
    .session-name {
        font-size: 14px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-left: 8px;
        flex-grow: 1;
    }
    .session-options-button {
        font-size: 16px;
        cursor: pointer;
        padding: 2px 6px;
        border-radius: 3px;
        font-weight: bold;
    }
    .session-options-button:hover {
        background-color: #555;
    }
    .options-menu {
        position: absolute;
        top: 100%;
        right: 0;
        background-color: #2a2a2a;
        border: 1px solid #555;
        border-radius: 4px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        display: none;
        z-index: 1000;
        width: 120px;
    }
    .options-menu.active {
        display: block;
    }
    .option {
        padding: 8px 12px;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    .option:hover {
        background-color: #444;
    }
    .rename-input {
        width: 100%;
        padding: 6px;
        margin-top: 5px;
        border: 1px solid #555;
        border-radius: 3px;
        background-color: #333;
        color: #f0f0f0;
    }
    .rename-confirm {
        margin-top: 5px;
        padding: 4px 8px;
        background-color: #4a8;
        border: none;
        border-radius: 3px;
        color: #fff;
        cursor: pointer;
    }
    .rename-confirm:hover {
        background-color: #5b9;
    }
    </style>
    """
    return html

# ----------------------------------------------
# JavaScript snippet in <head>, using <script> tags
# ----------------------------------------------
custom_js = """
<script>
document.addEventListener("click", function(e){
  // Handle session item clicks for loading chats
  var item = e.target.closest(".session-item");
  if (item && !e.target.closest(".session-options-button") && !e.target.closest(".options-menu")) {
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
    return;
  }
  
  // Close any open options menus when clicking elsewhere
  document.querySelectorAll('.options-menu.active').forEach(menu => {
    if (!menu.contains(e.target) && !e.target.closest(".session-options-button")) {
      menu.classList.remove('active');
    }
  });
  
  // Toggle options menu when clicking the options button
  if (e.target.closest(".session-options-button")) {
    e.stopPropagation(); // Prevent triggering the session-item click
    
    // Close all other menus first
    document.querySelectorAll('.options-menu.active').forEach(menu => {
      menu.classList.remove('active');
    });
    
    // Then open this one
    var optionsBtn = e.target.closest(".session-options-button");
    var index = optionsBtn.dataset.index;
    var menu = document.getElementById('options-menu-' + index);
    menu.classList.toggle('active');
  }
  
  // Handle rename option
  if (e.target.closest(".rename-option")) {
    e.stopPropagation();
    var index = e.target.closest(".rename-option").dataset.index;
    var sessionItem = document.querySelector(`.session-item[data-index="${index}"]`);
    var sessionName = sessionItem.querySelector(".session-name").textContent;
    
    // Create rename input UI
    var renameUI = document.createElement('div');
    renameUI.className = 'rename-ui';
    renameUI.innerHTML = `
      <input type="text" class="rename-input" value="${sessionName}" />
      <button class="rename-confirm">Save</button>
    `;
    
    // Replace the session name with the rename UI
    sessionItem.querySelector(".session-name").style.display = 'none';
    sessionItem.insertBefore(renameUI, sessionItem.querySelector(".session-options-button"));
    
    // Focus the input
    var input = renameUI.querySelector('.rename-input');
    input.focus();
    input.select();
    
    // Setup save button click
    renameUI.querySelector('.rename-confirm').addEventListener('click', function() {
      var newName = input.value.trim();
      if (newName) {
        // Call rename_callback with "index:new_name" format
        var hiddenBox = document.querySelector("#rename-callback textarea");
        if (hiddenBox) {
          hiddenBox.value = index + ":" + newName;
          hiddenBox.dispatchEvent(new Event("input", { bubbles: true }));
        }
      }
      
      // Close the menu
      document.getElementById('options-menu-' + index).classList.remove('active');
    });
    
    // Setup input Enter key
    input.addEventListener('keypress', function(ev) {
      if (ev.key === 'Enter') {
        renameUI.querySelector('.rename-confirm').click();
      }
    });
    
    // Close the menu
    document.getElementById('options-menu-' + index).classList.remove('active');
  }
  
  // Handle delete option
  if (e.target.closest(".delete-option")) {
    e.stopPropagation();
    var index = e.target.closest(".delete-option").dataset.index;
    
    if (confirm("Are you sure you want to delete this chat?")) {
      // Call delete_callback
      var hiddenBox = document.querySelector("#delete-callback textarea");
      if (hiddenBox) {
        hiddenBox.value = index;
        hiddenBox.dispatchEvent(new Event("input", { bubbles: true }));
      }
    }
    
    // Close the menu
    document.getElementById('options-menu-' + index).classList.remove('active');
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
/* Change chatbot message background */
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
            # Must have interactive=True + the correct elem_id
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
            
            # -- Rename a chat session
            rename_callback.input(
                rename_chat,
                inputs=[rename_callback, session_list],
                outputs=[session_list, session_html]
            )
            
            # -- Delete a chat session
            delete_callback.input(
                delete_chat,
                inputs=[delete_callback, session_list],
                outputs=[session_list, session_html]
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