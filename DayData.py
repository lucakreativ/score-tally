class DayData:
    def __init__(self, value = 0, exists = True):
        self.value = value
        self.exists = exists

    def convert_to_human_time(self):
        hours = self.value // 60
        minutes = self.value % 60
        return f"{hours:02d}:{minutes:02d}"

    def set_value(self, value):
        self.value = value

    def set_exists(self, exists):
        self.exists = exists

    def export_to_dict(self):
        if self.exists:
            return {'humanTime': self.value, 'value': self.value}
        else:
            return {'humanTime': self.convert_to_human_time(), 'value': 0}