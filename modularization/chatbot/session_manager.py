class SessionManager:
    def __init__(self):
        self.sessions = {}

    def add_session(self, session_name, session_data):
        self.sessions[session_name] = session_data

    def get_session(self, session_name):
        return self.sessions.get(session_name)

    def list_sessions(self):
        return list(self.sessions.keys())
