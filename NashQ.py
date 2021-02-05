import random
import numpy as np
import nashpy as nash

class NashQ:

    def __init__(self, player, alpha, gamma,epsilon, num_states, num_actions):
        self.player = player
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.num_actions = num_actions
        self.base_alpha = alpha
        self.Q = np.zeros((2, num_states, self.num_actions, self.num_actions))
        self.last_state = -1
        self.history_alpha = np.zeros((num_states, self.num_actions, self.num_actions))
        self.history_act = np.zeros((num_states, 1))


    def getMove(self, lastReward, lastMove, tick):
        value = self.select_action(tick)
        return value

    """calculate actions a^i_t"""
    def select_action(self,tick):
        state = self.last_state
        #select a random move with epsilon prob
        if random.random() < self.epsilon:
            choice = np.random.choice(np.arange(self.num_actions), 1)[0]
        #else calculate probs of executing moves and choose the next move
        else:
            A = self.Q[0, state]
            B = self.Q[1, state]
            rps = nash.Game(A, B)
            pi = list(rps.support_enumeration())
            pi = pi[0][0].tolist()
            #select the best move with the probability p
            choice = np.random.choice(np.arange(len(pi)), p=pi)

        return choice

    #get nash Equilibrium
    def nash_action(self, state, pi, pi_other, Q):
        nashq = 0
        for act1 in range(self.num_actions):
            for act2 in range(self.num_actions):
                nashq += pi[act1] * pi_other[act2] * Q[state][(act1, act2)]
        return nashq

    def update(self, own, other, nash_action, q, reward, state):
        self.history_alpha[state, own, other] += 1
        q_old = q[0, own, other]
        self.alpha = self.base_alpha / (self.history_alpha[state, own, other])
        if self.alpha < 0.001:
            self.alpha = 0.001

        # Qit+1(s,a1,a2) = (1−alpha) * Qit(s;a1,a2)+ alpha * [rit+ gamma * (NashQit(s')]
        updated_q = q_old + (self.alpha * (reward + (self.gamma * nash_action) - q_old))

        return updated_q

    """calculate pi nash"""
    def compute_pi(self, state):
        pl_1 = self.Q[0, state]
        pl_2 = self.Q[1, state]
        game = nash.Game(pl_1, pl_2)
        equil = game.support_enumeration()
        # equil = game.lemke_howson_enumeration()
        # equil = game.vertex_enumeration()
        pis = list(equil)
        pi = None
        for _pi in pis:
            if _pi[0].shape == (self.num_actions, ) and _pi[1].shape == (self.num_actions, ):
                if any(np.isnan(_pi[0])) is False and any(np.isnan(_pi[1])) is False:
                    pi = _pi
                    break

        if pi is None:
            pi1 = np.repeat(1.0 / self.num_actions, self.num_actions)
            pi2 = np.repeat(1.0 / self.num_actions, self.num_actions)
            pi = (pi1, pi2)

        return pi[0], pi[1]

#
    def getPlayer(self):
        return self.player
