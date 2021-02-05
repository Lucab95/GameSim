import random

class RandomAgent:

    def __init__(self, my_lambda):
        self.my_lambda = my_lambda
        pass

    def getMove(self):
        if random.random() < self.my_lambda:
            return 0
        else:
            return 1

    def update(self, OtherAction):
        pass

    def getClass(self):
        return "Random with {} = lambda".format(self.my_lambda)