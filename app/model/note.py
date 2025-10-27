from datetime import datetime

class Note:
    def __init__(self, id, author, content):
        self.id = id
        self.author = author
        self.content = content
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    def to_dict(self):
        return {
            "id": self.id,
            "author": self.author,
            "content": self.content,
            "timestamp": self.timestamp
        }
