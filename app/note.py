from datetime import datetime

class Note:
    def __init__(self, patientID, author, content):
        self.patientID = patientID
        self.author = author
        self.content = content
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    def to_dict(self):
        return {
            "patientID": self.patientID,
            "author": self.author,
            "content": self.content,
            "timestamp": self.timestamp
        }
