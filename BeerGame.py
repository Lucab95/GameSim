import random, SarsaBeer, collections, distribution
import numpy as np
import pandas as pd

class BeerGame:

    def __init__(self):
        self.inv_R = 12
        self.inv_F = 12

        self.backlog_R = 0
        self.backlog_F = 0

        self.cost_inv = 0.5
        self.cost_backlog = 1

        self.demand_cus = [4, 4, 4]
        for _ in range(49):
            self.demand_cus.append(8)

        self.orders_incoming_F = 4
        self.orders_placed_R = 4
        self.prod_request = 4
        self.delay2_F = 4
        self.delay1_F = 4
        self.prod_delay2 = 4
        self.prod_delay1 = 4

        self.cost_R = []
        self.cost_F = []

        self.picks_R = []
        self.picks_F = []

        self.choices = [0, 4, 10, 20, 30]

        self.forced = True
        self.distr = distribution.distribution(2)
        self.nextChoice = 0
        self.updateCount = 0

        self.Retailer = SarsaBeer.SarsaBeer("Retailer", 0.5, 0.9, 0.1, self.choices, 10, 5, 4)
        self.Factory = SarsaBeer.SarsaBeer("Factory", 0.5, 0.9, 0.1, self.choices, 10, 5, 4)
        weeks = 10000
        # making records for dataframe
        total_cost_R = []
        total_cost_F = []
        var_R = []
        var_F = []

        print('efe')
        for j in range(weeks):
            for i in range(len(self.demand_cus)):
                self.WeekLoop(i, i * j)
            if j % (weeks / 10) == 0 or j == weeks - 1:
                self.print(j)
            total_cost_R.append(sum(self.cost_R))
            total_cost_F.append(sum(self.cost_F))
            var_R.append(np.var(self.picks_R))
            var_F.append(np.var(self.picks_F))
            self.Initial()
            self.Initial()

        # output a csv to make analysis easier
        df = {
            'total_cost_R': total_cost_R,
            'total_cost_F': total_cost_F,
            'var_R': var_R,
            'var_F': var_F
        }

        df = pd.DataFrame(df)
        df.to_csv('FRAP2.csv')

    def Initial(self):
        self.inv_R = 12
        self.inv_F = 12

        self.backlog_R = 0
        self.backlog_F = 0
        self.orders_incoming_F = 4
        self.orders_placed_R = 4
        self.prod_request = 4
        self.delay2_F = 4
        self.delay1_F = 4
        self.prod_delay2 = 4
        self.prod_delay1 = 4

        self.cost_R = []
        self.cost_F = []

        self.picks_R = []
        self.picks_F = []

        self.nextChoice = 0
        self.updateCount = 0

    def WeekLoop(self, i, tick):
        # transfer
        self.inv_R += self.delay1_F
        self.inv_F += self.prod_delay1

        self.delay1_F = self.delay2_F
        self.prod_delay1 = self.prod_delay2

        # Fulfill orders
        if self.inv_R >= self.demand_cus[i] + self.backlog_R:
            self.inv_R -= self.demand_cus[i] + self.backlog_R
            self.backlog_R = 0
        else:
            self.backlog_R = self.demand_cus[i] + self.backlog_R - self.inv_R
            self.inv_R = 0

        if self.inv_F >= self.orders_incoming_F + self.backlog_F:
            self.inv_F -= self.orders_incoming_F + self.backlog_F
            self.delay2_F = self.orders_incoming_F + self.backlog_F
            self.backlog_F = 0
        else:
            self.backlog_F = self.orders_incoming_F + self.backlog_F - self.inv_F
            self.delay2_F = self.inv_F
            self.inv_F = 0

        # Transfer orders
        self.orders_incoming_F = self.orders_placed_R

        # Factory Orders
        self.prod_delay2 = self.prod_request

        # Player Costs
        curr_cost_R = self.inv_R * self.cost_inv + self.backlog_R * self.cost_backlog
        curr_cost_F = self.inv_F * self.cost_inv + self.backlog_F * self.cost_backlog


        # Players State
        if self.inv_R == 0:
            if self.backlog_R > 100:
                r_state = 9
            elif self.backlog_R > 50:
                r_state = 8
            elif self.backlog_R > 25:
                r_state = 7
            elif self.backlog_R > 10:
                r_state = 6
            else:
                r_state = 5
        else:
            if self.inv_R > 100:
                r_state = 4
            elif self.inv_R > 50:
                r_state = 3
            elif self.inv_R > 25:
                r_state = 2
            elif self.inv_R > 10:
                r_state = 1
            else:
                r_state = 0
        if self.inv_F == 0:
            if self.backlog_F > 100:
                f_state = 9
            elif self.backlog_F > 50:
                f_state = 8
            elif self.backlog_F > 25:
                f_state = 7
            elif self.backlog_F > 10:
                f_state = 6
            else:
                f_state = 5
        else:
            if self.inv_F > 100:
                f_state = 4
            elif self.inv_F > 50:
                f_state = 3
            elif self.inv_F > 25:
                f_state = 2
            elif self.inv_F > 10:
                f_state = 1
            else:
                f_state = 0


        # Players Choice and Update
        if self.forced:
            if i == self.nextChoice:
                self.orders_placed_R = self.Retailer.update(-curr_cost_R, r_state, tick, False)
                self.prod_request = self.Factory.update(-curr_cost_F, f_state, tick, False)
                self.nextChoice = i + self.distr.getNext()
                self.updateCount += 1
            else:
                _ = self.Retailer.update(-curr_cost_R, r_state, tick, True)
                _ = self.Factory.update(-curr_cost_F, f_state, tick, True)
        else:
            self.orders_placed_R = self.Retailer.update(-curr_cost_R, r_state, tick, False)
            self.prod_request = self.Factory.update(-curr_cost_F, f_state, tick, False)

        self.picks_R.append(self.orders_placed_R)
        self.picks_F.append(self.prod_request)

        # Record Cost
        self.cost_R.append(curr_cost_R)
        self.cost_F.append(curr_cost_F)

    def print(self,j):
        print("Iteration: ", j)
        print("Cost R: ", sum(self.cost_R),self.cost_R)
        print("Cost F: ", sum(self.cost_F),self.cost_F)
        print("Picks R: ", collections.Counter(self.picks_R), self.picks_R)
        print("Picks F: ", collections.Counter(self.picks_F), self.picks_F)
        if self.forced:
            print("Update Count: ", self.updateCount)
        self.Retailer.debug()
        self.Factory.debug()


def main():
    newGame = BeerGame()


if __name__ == "__main__":
    main()
