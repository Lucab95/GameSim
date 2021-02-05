import random

class SarsaBeer:

    def __init__(self, player, alpha, gamma, my_lambda, choices, states, first_state, first_action):
        self.player = player #Purely for Identification
        self.alpha = alpha
        self.gamma = gamma
        self.my_lambda = my_lambda
        self.choices = choices
        self.num_actions = len(choices)
        self.num_states = states
        self.Q = [[random.random()] * self.num_actions for _ in range(self.num_states)]
        self.e = [[0.0] * self.num_actions for _ in range(self.num_states)]
        self.last_state = first_state
        self.last_action = self.choices.index(first_action)

    def pickAction(self, tick, next_state):
        if tick == 0:
            epsilon = 1
        else:
            epsilon = 1/tick
        ep_chance = random.random()
        if ep_chance < epsilon:
            return self.choices.index(random.choice(self.choices))
        else:
            index = self.Q[next_state].index(max(self.Q[next_state]))
            return index

    def update(self, reward, next_state, tick, repeated):
        if not repeated:
            next_action = self.pickAction(tick, next_state)
        else:
            next_action = self.last_action
        delta = reward + self.gamma*self.Q[next_state][next_action] - self.Q[self.last_state][self.last_action]
        self.e[self.last_state][self.last_action] += 1
        for i in range(self.num_states):
            for j in range(self.num_actions):
                self.Q[i][j] += self.alpha * delta * self.e[i][j]
                self.e[i][j] *= self.gamma * self.my_lambda
        self.last_state = next_state
        if not repeated:
            self.last_action = next_action
        return self.choices[next_action]

    def debug(self):
        print("Player: ", self.player, "Q:", self.Q)