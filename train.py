from agent.agent import Agent
from functions import *
import sys
import datetime

from keras.callbacks import TensorBoard, EarlyStopping
time_list = []
first_time = datetime.datetime.now()
try:
	if len(sys.argv) != 4:
		print ("Usage: python train.py [stock] [window] [episodes]")
		exit()

	stock_name, window_size, episode_count = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
	# stock_name, window_size, episode_count = 'GSPC', 30, 10
	agent = Agent(window_size)
	data = getStockDataVec(stock_name)
	l = len(data) - 1
	batch_size = 32

	for e in range(episode_count + 1):
		print ("Episode " + str(e) + "/" + str(episode_count))
		state = getState(data, 0, window_size + 1)

		total_profit = 0
		agent.inventory = []

		for t in range(l):
			action = agent.act(state)

			# sit
			next_state = getState(data, t + 1, window_size + 1)
			reward = 0

			if action == 1: # buy
				agent.inventory.append(data[t])
				# print ("Buy: " + formatPrice(data[t]))

			elif action == 2 and len(agent.inventory) > 0: # sell
				bought_price = agent.inventory.pop(0)
				reward = max(data[t] - bought_price, 0)
				total_profit += data[t] - bought_price
				# print ("Sell: " + formatPrice(data[t]) + " | Profit: " + formatPrice(data[t] - bought_price))

			done = True if t == l - 1 else False
			agent.memory.append((state, action, reward, next_state, done))
			state = next_state

			if done:
				print ("--------------------------------")
				print ("Total Profit: " + formatPrice(total_profit))
				print ("--------------------------------")
				last_time = datetime.datetime.now()
				delta = last_time - first_time
				time_list.append(delta)
				print(delta.total_seconds())
				first_time = datetime.datetime.now()

			if len(agent.memory) > batch_size:
				agent.expReplay(batch_size)

		if e % 10 == 0:
			agent.model.save("models/model_ep" + str(e))
except Exception as e:
	print("Error occured: {0}".format(e))
finally:
	print(time_list)
	exit()