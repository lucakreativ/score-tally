class DayData:
    def __init__(self, value = 0, exists = True):
        self.value = value
        self.exists = exists

    def convert_to_human_time(self):
        hours = int(self.value)
        minutes = int((self.value * 60) % 60)
        return f"{hours}:{minutes:02d}"

    def set_value(self, value):
        self.value = value

    def set_exists(self, exists):
        self.exists = exists

    def export_to_dict(self):
        if self.exists:
            return {'humanTime': self.convert_to_human_time(), 'value': self.value}
        else:
            return {'humanTime': '', 'value': 0}