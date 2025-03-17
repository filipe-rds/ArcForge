
import uuid
from arcforge.core.conn.request import Request


class Session:
    """
    Classe responsável pelo gerenciamento de sessões e cookies.
    """
    sessions = {}

    def __init__(self, request: Request):
        self.session_id = request.cookies.get("session_id", str(uuid.uuid4()))
        self.data = self.sessions.get(self.session_id, {})
        self.sessions[self.session_id] = self.data

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value

    def delete(self):
        if self.session_id in self.sessions:
            del self.sessions[self.session_id]
    
    def get_cookies(self):
        return {"session_id": self.session_id} if self.session_id else {}
