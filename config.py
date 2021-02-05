from pathlib import Path

general = {
    "game": "MP",  # accepted values: {"MP","PD"}
    "method": "WoLF",  # accepted values  {"WoLF","NashQ"}

    "periods": 100000,


    "repeated_action_type": 3,  # type of forced repeated action
    # if repeated_action_type = 1 no repeated action pairs are applied
    # if repeated_action_type = 2 the algorithm, choose an action, this action is forced to be repeated n times.
    #   then a new action gets chosen and it gets repeated 'n' times, n is the output value of the poisson distribution.
    #   Note: a new 'n' is calculated every time.
    # if repeated_action_type = 3  a specific move is forced to happen with a lambda probability

}
if general["repeated_action_type"] == 3:
    repeat = {
        "forced_action": [0, 0],  # action to force
        "lambda_value": 0.0,  # probability of forcing an action after a player choose the same action as
                              # "forced_action"
        "repeat_m_times": 1,  # number of times to force the repetition
    }

if general["method"] == "WoLF":
    params = {
        "alpha": 0.1,
        "gamma": 1.0,
        "D_win": 0.001,  # delta win
        "D_lose": 0.002,  # delta lose
    }
elif general["method"] == "NashQ":
    params = {
        "alpha": 0.1,
        "gamma": 0.6,
        "epsilon": 1,
    }

DEBUG = False  # Make the algortihm print information about pi
print_every = 100  # define the range of steps to print the pi
