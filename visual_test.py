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

def generate_chat_name():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def chatbot_response(user_input, chat_history, selected_context):
    if isinstance(user_input, dict):  # e.g., user uploaded a file
        user_text = user_input.get("text", "")
    else:
        user_text = user_input  

    if not user_text.strip():
        return chat_history, "" 

    context_description = RAG_CONTEXTS.get(selected_context, "General Chatbot")
    bot_reply = f"[{selected_context} Context] {context_description} - You asked: '{user_text}'"

    updated_history = list(chat_history)
    updated_history.append({"role": "user", "content": user_text})
    updated_history.append({"role": "assistant", "content": bot_reply})

    return updated_history, ""

# ---------------- UI Updates ----------------
custom_js = """
<script>
document.addEventListener("DOMContentLoaded", function() {
    var sendButton = document.querySelector("#send-btn");
    
    if (sendButton) {
        sendButton.addEventListener("click", function() {
            setTimeout(() => {
                sendButton.innerText = "⏹ Interrupt";
            }, 100);
        });
    }
});
</script>
"""

# --------------------------------------------
# Gradio UI Setup
# --------------------------------------------
with gr.Blocks(
    head=custom_js,
    theme=gr.themes.Base(primary_hue="blue", neutral_hue="gray"),
    css="""
    html, body, .gradio-container {
        height: 100vh;
        margin: 0;
        overflow: hidden;
    }
    .gradio-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .gr-block {
        width: 100%;
        max-width: 1200px;
    }
    .chat-area {
        display: flex;
        flex-direction: column;
        height: 85vh;
        width: 100%;
    }
    .input-area {
        display: flex;
        width: 100%;
        padding: 10px;
        background-color: #1e1e1e;
    }
    #send-btn {
        min-width: 80px;
        background-color: #007bff;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    #send-btn:hover {
        background-color: #0056b3;
    }
"""
) as demo:
    
    with gr.Row(elem_classes=["chat-area"]):
        chatbot = gr.Chatbot(label="Chatbot")

    with gr.Row(elem_classes=["input-area"]):
        message_input = gr.Textbox(show_label=False, placeholder="Type your message here...", scale=10)
        send_btn = gr.Button("Send", elem_id="send-btn", scale=2)

    chat_history = gr.State([])

    def handle_message(user_input, history):
        new_history, _ = chatbot_response(user_input, history, "Science")
        return new_history, ""

    send_btn.click(
        handle_message,
        inputs=[message_input, chat_history],
        outputs=[chatbot, message_input]
    ).then(
        lambda x: x,
        inputs=[chatbot],
        outputs=[chat_history]
    )

    demo.load(
        lambda: [{"role": "assistant", "content": "👋 Welcome! Type something to start a conversation."}],
        outputs=[chatbot]
    )

demo.launch()
