from typing import List, Dict, Any, Tuple
import os

class ChatHistory:
    def __init__(self):
        self.history = []

    def add(self, msg: Dict[str, str]): # msg: {"role": "user", "text": "hello"}
        self.history.append(msg)

    def clear(self):
        self.history = []

    def __str__(self):
        return str(self.history)

    def __repr__(self):
        return str(self.history)

all_sessions_id = [] # 所有的session id
sid2history = {}  # session id 到历史记录的映射

filename2faiss = {}

all_sessions_id.append("for_testing")  # for testing
sid2history["for_testing"] = ChatHistory()
sid2history["for_testing"].add({"role": "ai", "text": "你好，我是图书推荐机器人，你可以问我关于图书的问题。"})

ALLOWED_EXTENSIONS = {'pdf', 'txt', 'md'}

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")