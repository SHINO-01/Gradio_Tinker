import gradio as gr
from chatbot.chatbot_logic import Chatbot
from chatbot.ui_components import build_ui, create_session_html
import base64

# Initialize chatbot
chatbot = Chatbot()


with open("W3_Nobg.png", "rb") as img_file:
    base64_str = base64.b64encode(img_file.read()).decode()

markdown_content = f"""
<h1 style="display: flex; align-items: center; gap: 10px;">
    <img src="data:image/png;base64,{base64_str}" width="40"/>W3 BrainBot
</h1>
"""

# Build UI with chatbot component
with gr.Blocks(
    head=open('modularization/static/js/custom.js').read(),
    theme=gr.themes.Base(primary_hue="blue", neutral_hue="gray", text_size=gr.themes.sizes.text_md),
    css=open('modularization/static/css/styles.css').read(),
) as demo:
    
    # Sidebar components
    with gr.Row(min_height=700):
        # Sidebar Column
        with gr.Column(scale=1, elem_classes=["sidebar"], min_width=250):
            gr.Markdown(markdown_content)
            new_chat_btn = gr.Button("➕  New Chat", elem_classes=["new-chat-btn", "spaced-icon-btn"], interactive=False)
            session_list = gr.State([])  
            session_html = gr.HTML("<div class='session-list'></div>")

            # Hidden textbox for session selection
            session_select_callback = gr.Textbox(
                elem_id="session-select-callback", visible=False, interactive=True
            )

        # Main Chat UI Column
        with gr.Column(min_width=1100, scale=30, elem_classes=["main-chat-ui"]):
            chatbot_component = gr.Chatbot(
                show_label=False, type="messages", min_height=790, min_width=600, height=650,
                container=False, avatar_images=["USR_small.png", "W3_Nobg_ssmall.png"], layout="bubble"
            )

            with gr.Row():
                message_input = gr.MultimodalTextbox(
                    show_label=False, placeholder="Type your message here...", scale=10,
                    elem_id="message-input", max_plain_text_length=8000, max_lines=8000
                )

            chat_history = gr.State([])

            def handle_message(user_input, history, session_list):
                """Handle message input from user and update session HTML"""
                user_text = str(user_input).strip() if not isinstance(user_input, dict) else user_input.get("text", "").strip()

                if not user_text:
                    return history, "", session_list, session_html

                # Ensure session creation and processing of user message
                if len(history) == 0:
                    chat_name = chatbot.generate_chat_name()
                    session_list = list(session_list)
                    if chat_name not in chatbot.chat_sessions:
                        chatbot.chat_sessions[chat_name] = [{"role": "assistant", "content": "👋 Welcome to W3 BrainBot!"}]
                        session_list.append(chat_name)

                new_history, _ = chatbot.chatbot_response(user_text, history)
                new_history.append({"role": "user", "content": user_text})

                if len(history) == 0:
                    chatbot.chat_sessions[chat_name] = new_history  # Save first message

                # Update session HTML after handling the message
                session_html = create_session_html(session_list)

                return new_history, "", session_list, session_html

            message_input.submit(
                handle_message,
                inputs=[message_input, chat_history, session_list],
                outputs=[chatbot_component, message_input, session_list, session_html]
            ).then(
                lambda: gr.update(interactive=True), outputs=[new_chat_btn]
            )

            # New Chat Button
            new_chat_btn.click(
                chatbot.start_new_chat,
                inputs=[chat_history, session_list],
                outputs=[chatbot_component, chat_history, session_list, session_html]
            ).then(
                lambda: gr.update(interactive=False), outputs=[new_chat_btn]
            )

            # Loading past session
            session_select_callback.input(
                chatbot.load_chat, inputs=[session_select_callback, session_list], outputs=[chatbot_component]
            )

