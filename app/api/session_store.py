import uuid

_sessions = {}

def create_session(state: dict) -> str:
    session_id = str(uuid.uuid4())
    _sessions[session_id] = state
    return session_id

def get_session(session_id: str):
    return _sessions.get(session_id)

def update_session(session_id: str,state: dict):
    _sessions[session_id] = state

def delete_session(session_id: str):
    _sessions.pop(session_id,None)