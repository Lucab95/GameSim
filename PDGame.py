import distribution, TitForTat, RandomAgent
FIRST = True

class PDGame:

    def __init__(self, topLeft, topRight, bottomLeft, bottomRight, forced, first, my_lambda=0.5):
        self.topLeft = topLeft
        self.topRight = topRight
        self.bottomLeft = bottomLeft
        self.bottomRight = bottomRight
        self.game = [[self.topLeft, self.topRight], [self.bottomLeft, self.bottomRight]]
        self.distr = distribution.distribution(2)
        self.forced = forced
        if first:
            self.playerOne = TitForTat.TitForTat()
            self.playerTwo = RandomAgent.RandomAgent(my_lambda)
        else:
            self.playerOne = RandomAgent.RandomAgent(my_lambda)
            self.playerTwo = TitForTat.TitForTat()

    def loop(self):
        self.tick = 0
        self.updateC = 0
        self.nextAction = 0
        self.iterations = 10000
        self.rewardOne = []
        self.rewardTwo = []
        while self.tick < self.iterations:
            if self.forced:
                if self.tick == self.nextAction:
                    actionOne = self.playerOne.getMove()
                    actionTwo = self.playerTwo.getMove()
                    self.nextAction = self.tick + self.distr.getNext()
                    self.updateC+=1
            else:
                actionOne = self.playerOne.getMove()
                actionTwo = self.playerTwo.getMove()
                self.nextAction = self.tick + self.distr.getNext()

            self.rewardOne.append(self.game[actionOne][actionTwo][0])
            self.rewardTwo.append(self.game[actionOne][actionTwo][1])

            self.playerOne.update(actionTwo)
            self.playerTwo.update(actionOne)

            self.tick += 1

    def finalPrint(self):
        print("Player One: {}, Total Reward: {}, Reward: {}".format(self.playerOne.getClass(), sum(self.rewardOne), self.rewardOne))
        print("Player Two: {},  Total Reward: {}, Reward: {}".format(self.playerTwo.getClass(), sum(self.rewardTwo), self.rewardTwo))
        print("Number of updates: {}".format(self.updateC))

def main():
    newGame = PDGame([5, 5], [0, 6],
                   [6, 0], [1, 1], True, FIRST, 0.9) #prisoner dilemma
    newGame.loop()
    newGame.finalPrint()

if __name__ == "__main__":
    main()