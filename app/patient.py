class Patient:
    def __init__(self, patientID, name, disease, high_risk=False):
        self.patientID = patientID
        self.name = name
        self.disease = disease
        self.high_risk = high_risk

    def to_dict(self):
        return {
            "patientID": self.patientID,
            "name": self.name,
            "disease": self.disease,
            "high_risk": self.high_risk
        }
