import datetime
from sentence_transformers import SentenceTransformer
import base64
import time

class Chatbot:
    def __init__(self):
        self.chat_sessions = {}
        self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')  # Example model

    def generate_chat_name(self):
        """Generate a unique chat session name based on current time"""
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def chatbot_response(self, user_input, chat_history):
        """Generate a response for the chatbot."""
        if isinstance(user_input, dict):  # Handle multimodal input
            user_text = user_input.get("text", "")
        else:
            user_text = user_input.strip()

        if not user_text:
            return chat_history, ""  # Ignore empty input

        bot_reply = f"You asked: '{user_text}'"
        updated_history = list(chat_history)
        updated_history.append({"role": "user", "content": user_text})
        
        if not bot_reply.strip():
            bot_reply = " "

        updated_history.append({"role": "assistant", "content": bot_reply})
        return updated_history, ""  # No flickering

    def start_new_chat(self, chat_history, session_list):
        """Start a new chat and save the session."""
        if chat_history:
            chat_name = self.generate_chat_name()
            self.chat_sessions[chat_name] = list(chat_history)
            if chat_name not in session_list:
                session_list.append(chat_name)
        welcome_message = "🔄 New chat started!"
        return [{"role": "assistant", "content": welcome_message}], [], session_list

    def load_chat(self, selected_index_str, session_list):
        """Load a past chat by index."""
        try:
            idx = int(selected_index_str)
            if 0 <= idx < len(session_list):
                chat_name = session_list[idx]
                if chat_name in self.chat_sessions:
                    return self.chat_sessions[chat_name]
        except (ValueError, TypeError):
            pass
        return []  # Return empty if invalid selection
