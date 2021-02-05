To launch the project just install:

	pip install matplotlib
	pip install numpy
	pip install scipy
	pip install nashpy

- To launch the first version of the simulator use Game.py, this version included the prisoner dilemma and the matching pennies game with forced repeated action pairs

	If you want to change the behaviour of this simulation then the file config.py can be modifie
	
	
	############  CONFIG ################# 
	
	global parameters tips:

		"game":   		# Select the game that need to be explored 		-> accepted values: {"MP","PD"}, 
    		"method": 	 	# Select the Q-learning algorithm to use   		-> accepted values:  {"WoLF","NashQ"}
    		"periods": 		# define the number of periods/ticks to repeat the game 
    		"repeated_action_type": # Define the type of forced repeated actions to apply   -> accepted values: {1,2,3}
						1 - no forced repeated action pairs are applied
						2 - the algorithm choose an action and it gets repeated n times, where n is a value coming from the poisson distribution
						3 - a specific move "forced_action" is forced to happen with a lamba probability, this action is repeated "repeat_m_times" times
	specific parameter tips:
		"forced_action": 	# define the action that needs to be forced 		-> accepted values: {[0,0],[0,1],[1,0],[1,1]}
		"lambda_value" :	# probability of forcing an action after a player choose the same action as "forced_action"
		"repeat_m_times": 	# number of times to force the repetition

- To launch the second version of the simulator use BeerGame.py

- To launch the PD and TitForTat version of the simulator, launch PDGame. 
	It includes a global boolean variable "FIRST" which defines the first player as Tit-for-Tat and RandomAgent as second player if FIRST is equal to True.
	If FIRST is equal to False, first player is RandomAgent and second player is Tit-for-Tat
																									