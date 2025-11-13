class Storage:
    def __init__(self):
        self.data = {}

    def save(self, key: str, value):
        self.data[key] = value

    def load(self, key: str):
        return self.data.get(key)
