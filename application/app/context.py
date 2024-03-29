import os


class Context:
    visitedPages = set()
    startUrl = "https://nos.twnsnd.co/"
    directory = 'images'
    database_url = "postgresql://danila:Danila241201@db:5432/my_db"
    def init_visited_pages(self):
        # if we already have visited urls
        if os.path.exists("visitedURL.txt"):
            with open("visitedURL.txt", "r") as f:
                self.visitedPages = set(f.read().splitlines())
    def make_directory(self):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

ctx = Context()