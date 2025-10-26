class Schedule:
    def __init__(self, carestaffID, task, date):
        self.carestaffID = carestaffID
        self.task = task
        self.date = date

    def to_dict(self):
        return {
            "carestaffID": self.carestaffID,
            "task": self.task,
            "date": self.date
        }
