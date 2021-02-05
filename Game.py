import WoLF
import distribution
from NashQ import NashQ
import numpy as np
import random
import nashpy as nash
import matplotlib.pyplot as plt
import config as cfg

# global variables and parameters can be changed through the config.py file
GAME = cfg.general["game"]
METHOD = cfg.general["method"]
PERIODS = cfg.general["periods"]

REPEATED_ACTION_TYPE = cfg.general["repeated_action_type"]
if REPEATED_ACTION_TYPE == 3:
    REPEAT_M_TIMES = cfg.repeat["repeat_m_times"]
    LAMBDA_VALUE = cfg.repeat["lambda_value"]
    FORCED_ACTION = cfg.repeat["forced_action"]


def updateNash(player, actions, nash_actions, nash_actions_opp, rewards, tick):
    player.Q[0, 0, actions[0], actions[1]] = player.update(actions[player.player], actions[1 - player.player],
                                                           nash_actions, player.Q[0], rewards[0], 0)
    player.Q[1, 0, actions[1], actions[0]] = player.update(actions[1 - player.player], actions[player.player],
                                                           nash_actions_opp, player.Q[1], rewards[1], 0)
    player.epsilon = 1 / tick
    # player.epsilon *= player.epsilon * 0.999
    if player.epsilon < 0.01:
        player.epsilon = 0.01
    return player


def forceRepeat(canbe_repeated, tick, force):
    if force:
        return True
    if REPEATED_ACTION_TYPE == 3 and canbe_repeated == tick and random.random() < LAMBDA_VALUE:
        return True
    else:
        return False


class Game:

    def __init__(self, topLeft, topRight, bottomLeft, bottomRight):
        self.topLeft = topLeft
        self.topRight = topRight
        self.bottomLeft = bottomLeft
        self.bottomRight = bottomRight
        self.game = [[self.topLeft, self.topRight], [self.bottomLeft, self.bottomRight]]
        self.distr = distribution.distribution()
        if METHOD == 'WoLF':
            self.playerOne = WoLF.WoLF(0, cfg.params["alpha"], cfg.params["gamma"], cfg.params["D_win"],
                                       cfg.params["D_lose"], num_states=1, num_actions=2)
            self.playerTwo = WoLF.WoLF(1, cfg.params["alpha"], cfg.params["gamma"], cfg.params["D_win"],
                                       cfg.params["D_lose"], num_states=1, num_actions=2)
        else:
            self.playerOne = NashQ(0, cfg.params["alpha"], cfg.params["gamma"], cfg.params["epsilon"], num_states=1,
                                   num_actions=2)
            self.playerTwo = NashQ(1, cfg.params["alpha"], cfg.params["gamma"], cfg.params["epsilon"], num_states=1,
                                   num_actions=2)
        self.players1_hist = []
        self.players2_hist = []
        self.tick = 0
        self.countMoves = np.zeros((2, 2))  # (num_player, num_actions)
        self.move_repeated_m_times = 0

    # take reward for the single player
    def getMoveReward(self, onePick, twoPick, player):
        return self.game[onePick][twoPick][player]

    # take the rewards together
    def getMovesReward(self, onePick, twoPick):
        return self.game[onePick][twoPick]

    # def getMoveValues(self, onePick, twoPick):
    #     return self.game[onePick][twoPick]

    def startLoop(self):
        onePick = self.playerOne.getMove(0, [0, 0], 0)
        twoPick = self.playerTwo.getMove(0, [0, 0], 0)
        self.tick += 1
        self.nextMove = self.tick + self.distr.getNext()
        self.loop(onePick, twoPick)

    def loop(self, onePick, twoPick):
        canbe_repeated = 0
        updateCount = 0
        action_forced = 0
        players = [self.playerOne, self.playerTwo]
        player1_move_hist = []
        player2_move_hist = []
        actions = []
        rewards = self.getMovesReward(onePick, twoPick)
        force = False
        while (self.tick < PERIODS):

            if not REPEATED_ACTION_TYPE == 2:  # activate or deactivate repeated action pairs
                self.nextMove = self.tick

            # begin WoLF part
            if METHOD == 'WoLF':
                if self.tick % 2 == 0 and REPEATED_ACTION_TYPE == 3:
                    self.playerOne.resetQ()
                    self.playerTwo.resetQ()
                if self.tick == self.nextMove:

                    # check if the actions has to /could be repeated
                    if forceRepeat(canbe_repeated, self.tick, force):
                        # after first repetition, the action it is forced to be repeated REPEAT_M_TIMES
                        force = True
                        self.move_repeated_m_times += 1
                        action_forced += 1
                        onePick, twoPick = FORCED_ACTION
                        if cfg.DEBUG:
                            print("action forced:", FORCED_ACTION, "period:", self.tick)

                    else:  # calculate new moves
                        updateCount += 1  # counts how many new moves are calculated
                        onePick = self.playerOne.getMove(
                            self.getMoveReward(onePick, twoPick, self.playerOne.getPlayer()), [onePick, twoPick],
                            self.tick)
                        twoPick = self.playerTwo.getMove(
                            self.getMoveReward(onePick, twoPick, self.playerTwo.getPlayer()), [onePick, twoPick],
                            self.tick)
                    self.nextMove = self.tick + self.distr.getNext()

                    # calculate players pi and save history
                for i, player in enumerate(players):
                    pi, _ = player.compute_pi(0)
                    if cfg.DEBUG and self.tick % cfg.print_every == 0:
                        print("Player", i, "period:", self.tick, "pi:", np.round(pi, 5))
                    if i == 0:
                        self.players1_hist.append((pi[0], pi[1]))
                    else:
                        self.players2_hist.append((pi[0], pi[1]))
                self.playerOne.update(onePick, 0, self.getMoveReward(onePick, twoPick, self.playerOne.getPlayer()))
                self.playerTwo.update(twoPick, 0, self.getMoveReward(onePick, twoPick, self.playerTwo.getPlayer()))
            # end WoLF part

            # else: begin NashQ part
            elif METHOD == 'NashQ':
                # calculate new action
                if self.tick == self.nextMove or self.tick == 1:
                    actions = []

                    # choose action
                    # if forceRepeat is true, force the defined action
                    if forceRepeat(canbe_repeated, self.tick, force):
                        force = True
                        self.move_repeated_m_times += 1
                        action_forced += 1  # count the number of moves forced
                        actions = FORCED_ACTION
                        if cfg.DEBUG:
                            print("Action forced:", FORCED_ACTION, "period:", self.tick)

                    # otherwise, calculate a new move according to epsilon
                    else:
                        updateCount += 1  # counts how many new moves are calculated
                        for player in players:
                            actions.append(player.select_action(self.tick))

                    onePick, twoPick = actions
                    self.nextMove = self.tick + self.distr.getNext()  #
                    rewards = self.getMovesReward(onePick, twoPick)

                players_update = []
                # observe and update
                for i, player in enumerate(players):
                    # calculate players pi and save history
                    pi, pi_opp = player.compute_pi(0)
                    if cfg.DEBUG and self.tick % cfg.print_every == 0:
                        print("Player", i, "period:", self.tick, "pi:", np.round(pi, 5))
                    if i == 0:
                        self.players1_hist.append(pi)
                    else:
                        self.players2_hist.append(pi)

                    # calculate best strategy for the player
                    nash_actions = player.nash_action(0, pi, pi_opp, player.Q[0])
                    nash_actions_opp = player.nash_action(0, pi_opp, pi, player.Q[1])

                    # update according to the other player
                    players_update.append(
                        updateNash(player, actions, nash_actions, nash_actions_opp, rewards, self.tick))
                players = players_update
            # end NashQ part

            self.countMoves[0, onePick] += 1
            self.countMoves[1, twoPick] += 1
            player1_move_hist.append(onePick)
            player2_move_hist.append(twoPick)
            self.tick += 1
            if REPEATED_ACTION_TYPE == 3:
                if [onePick, twoPick] == FORCED_ACTION and canbe_repeated != self.tick - 1 and not force:
                    canbe_repeated = self.tick
                if force:
                    if self.move_repeated_m_times == REPEAT_M_TIMES:
                        if cfg.DEBUG:
                            print("move forced:", self.move_repeated_m_times, "times, new move will be chosen by the "
                                                                              "algorithm")
                        force = False
                        self.move_repeated_m_times = 0

        # end while -> prints and results plotting
        if METHOD == 'WoLF':
            self.playerOne.printpi(self.tick)
            self.playerTwo.printpi(self.tick)
        print("Player 0: ", "Pick: ", onePick, "Reward:",
              self.getMoveReward(onePick, twoPick, self.playerOne.getPlayer()), "Tick: ", self.tick)
        print("Player 1: ", "Pick: ", twoPick, "Reward:",
              self.getMoveReward(onePick, twoPick, self.playerTwo.getPlayer()))
        print(f"Number of Selections: {updateCount}")
        if cfg.general["repeated_action_type"] == 2:
            action_repeated = cfg.general["periods"] - updateCount-1
            print(f"Number of repeated actions: {action_repeated}")
        elif cfg.general["repeated_action_type"] == 3:
            print(f"Number of forced actions: {action_forced}")
        print("player 1 played:", int(self.countMoves[0][0]), int(self.countMoves[0][1]))
        print("player 2 played:", int(self.countMoves[1][0]), int(self.countMoves[1][1]))
        print("player 1 first 50 moves", player1_move_hist[0:50])
        print("player 2 first 50 moves", player2_move_hist[0:50])
        plotPi(self.players1_hist, self.players2_hist, 1)
        plotPi(self.players1_hist, self.players2_hist, 2)


def plotPi(hist1, hist2, strategy):
    pi1 = [item[strategy - 1] for item in hist1]
    pi2 = [item[strategy - 1] for item in hist2]
    if GAME == "PD":
        move = "C" if strategy == 1 else "D"
    elif GAME == "MP":
        move = "H" if strategy == 1 else "T"

    plt.plot(np.arange(len(pi1)),
             pi1, label="pi player 1 move:" + move)
    plt.plot(np.arange(len(pi2)),
             pi2, label="pi player 2 move:" + move)
    plt.xlabel("episode")
    plt.ylabel("pi of playing:" + move)
    plt.ylim(0, 1)
    plt.legend()
    plt.savefig("result" + move + ".jpg", dpi=400)
    plt.show()


def main():
    if GAME == "PD":
        newGame = Game([5, 5], [0, 6],
                       [6, 0], [1, 1])  # prisoner dilemma
    elif GAME == "MP":
        newGame = Game([1, -1], [-1, 1],
                       [-1, 1], [1, -1])  # matching pennies
    newGame.startLoop()


if __name__ == "__main__":
    main()
