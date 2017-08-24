class UltimateGuitarLink:
    link = ""
    transposition = 0

    def __init__(self, link, transposition=0):
        self.link = link
        self.transposition = transposition

    def get_link(self):
        return self.link

    def get_transposition(self):
        return self.transposition
