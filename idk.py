import gradio as gr
import datetime
import chromadb
from sentence_transformers import SentenceTransformer
import json

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection("chat_sessions")

# Load the embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Global variable to track the current active session
active_session_name = None  # Stores the name of the loaded session

def store_chat_session(session_name, chat_history):
    if not chat_history:
        return

    chat_texts = [f"{msg['role']}: {msg['content']}" for msg in chat_history]
    session_text = " ".join(chat_texts)
    embedding = embedding_model.encode(session_text).tolist()

    # Check if session exists
    existing_sessions = collection.get([session_name])

    if existing_sessions["ids"]:  # Update existing session
        collection.update(
            ids=[session_name],
            embeddings=[embedding],
            metadatas=[{"session_name": session_name, "history": json.dumps(chat_history)}]
        )
        print(f"[DEBUG] Updated session: {session_name}")
    else:  # Add new session
        collection.add(
            ids=[session_name],
            embeddings=[embedding],
            metadatas=[{"session_name": session_name, "history": json.dumps(chat_history)}]
        )
        print(f"[DEBUG] Stored new session: {session_name}")

def get_all_sessions():
    results = collection.get()
    if results and results["metadatas"]:
        return [meta["session_name"] for meta in results["metadatas"]]
    return []

def retrieve_similar_sessions(query):
    query_embedding = embedding_model.encode(query).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=3)

    if results and results["metadatas"][0]:
        return [json.loads(meta["history"]) for meta in results["metadatas"][0]]
    
    return []

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
    global active_session_name  # Reset active session

    if chat_history:
        if active_session_name:  # If editing an existing chat, update it
            store_chat_session(active_session_name, chat_history)
        else:  # Otherwise, create a new chat session
            chat_name = generate_chat_name()
            store_chat_session(chat_name, chat_history)
            session_list.append(chat_name)

    active_session_name = None  # Reset since it's a new chat

    welcome_message = f"🔄 New chat started with **{selected_context}** context!"
    return [{"role": "assistant", "content": welcome_message}], [], session_list, create_session_html(session_list)

# ---------------------------------------------
# Load a past chat by index from 'session_list'
# ---------------------------------------------
# Function to retrieve and set the active session
def load_chat(selected_index_str, session_list):
    global active_session_name

    if session_list:
        session_name = session_list[int(selected_index_str)]
        results = collection.get([session_name])

        if results["metadatas"]:
            active_session_name = session_name  # Set active session
            print(f"[DEBUG] Loaded session: {session_name}")
            return json.loads(results["metadatas"][0]["history"])

    return []


def handle_message(user_input, history, context):
    global active_session_name

    new_history, _ = chatbot_response(user_input, history, context)

    if active_session_name:  # If editing an existing chat, update it
        store_chat_session(active_session_name, new_history)

    return new_history, ""
def preload_sessions():
    sessions = get_all_sessions()
    session_html = create_session_html(sessions)
    return sessions, session_html

# Function to restore last active chat session on refresh
def restore_last_chat():
    global active_session_name

    sessions = get_all_sessions()
    if sessions:
        active_session_name = sessions[-1]  # Load the latest session
        results = collection.get([active_session_name])
        if results["metadatas"]:
            print(f"[DEBUG] Restoring last session: {active_session_name}")
            return json.loads(results["metadatas"][0]["history"]), active_session_name, sessions, create_session_html(sessions)

    return [], None, sessions, create_session_html(sessions)

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
    with gr.Blocks() as demo:
        with gr.Row(min_height=700):
            with gr.Column(scale=1, elem_classes=["sidebar"], min_width=250):
                gr.Markdown("## 📁 Chat History")

                new_chat_btn = gr.Button("➕ New Chat", elem_classes=["new-chat-btn"])
                session_list = gr.State([])  # Stores list of past sessions
                session_html = gr.HTML("<div class='session-list'>No saved chats yet</div>")
                active_session_state = gr.State(None)  # Stores active session name

                session_select_callback = gr.Textbox(
                    elem_id="session-select-callback",
                    visible=False,
                    interactive=True
                )

            with gr.Column(min_width=1100, scale=30):
                gr.Markdown("# 🤖 Chatbot with RAG Embedding Context")

                context_selector = gr.Dropdown(
                    choices=list(RAG_CONTEXTS.keys()),
                    value="Science",
                    label="Select Embedding Context"
                )

                chatbot = gr.Chatbot(label="Chatbot", type="messages")
                message_input = gr.Textbox(placeholder="Type your message here...")
                send_btn = gr.Button("Send")

                chat_history = gr.State([])

                # -- Load stored sessions on app launch --
                demo.load(preload_sessions, outputs=[session_list, session_html])

                # -- Restore last session after refresh --
                demo.load(
                    restore_last_chat,
                    outputs=[chatbot, active_session_state, session_list, session_html]
                )

                # -- Send message handler --
                send_btn.click(
                    handle_message,
                    inputs=[message_input, chat_history, context_selector],
                    outputs=[chatbot, message_input]
                ).then(
                    lambda x: x,
                    inputs=[chatbot],
                    outputs=[chat_history]
                )

                # -- Start new chat handler --
                new_chat_btn.click(
                    start_new_chat,
                    inputs=[context_selector, chat_history, session_list],
                    outputs=[chatbot, chat_history, session_list, session_html]
                )

                # -- Load past session handler --
                session_select_callback.input(
                    load_chat,
                    inputs=[session_select_callback, session_list],
                    outputs=[chatbot]
                ).then(
                    lambda x: x,
                    inputs=[chatbot],
                    outputs=[chat_history]
                )

    demo.launch()

