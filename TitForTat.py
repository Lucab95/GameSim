class TitForTat:

    def __init__(self):
        self.lastMove = 0

    def update(self, otherMove):
        self.lastMove = otherMove

    def getMove(self):
        return self.lastMove

    def getClass(self):
        return "TitForTat"