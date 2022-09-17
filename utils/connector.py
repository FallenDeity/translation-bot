from databases.mongo import Library, Blocker


class Mongo:
    def __init__(self):
        self.library = Library()
        self.blocker = Blocker()
