## Agent-Based Model of an Economy
## File: gold_withtax.py
## Author: Dustin A. Landers

from random import *
from math import *
import matplotlib.pyplot as pyplot
from numpy import *

##  The purpose of this project is to look at various tax models under a 
##      simple agent-based economic model
##  There is a grid with certain percentage of squares covered by gold nuggets
##  Each agent, called a wiggling :), moves around on the grid and tries to get as much 
##      gold as possible. They can only see the squares directly around them.   
##  After each iteration, a tax is applied.
##  That tax is then redistributed throughout all wigglings

grid_height = 100
grid_width = 100
percent_with_gold = 0.4

class Grid:

	""" Defines a grid with a specified width/height; locations of gold are specified randomly """
	
	def __init__(self, grid_height=grid_height, grid_width=grid_width, percent_with_gold=percent_with_gold):
		self.grid_height = grid_height
		self.grid_width = grid_width
		self.percent_with_gold = percent_with_gold
		self.locations = self.make_locations()
		
	def make_locations(self):
		d = dict()
		for i in range(self.grid_width):
			for j in range(self.grid_height):
				d[i,j] = 0
		amount = ceil(self.percent_with_gold * len(d))
		count = 1
		while count < amount:
			count += 1
			d[randint(0, self.grid_width - 1), randint(0, self.grid_height - 1)] = 1
		return(d)
		
	def how_much(self):
		how_much_gold = 0
		for i in range(self.grid_height):
			for j in range(self.grid_width):
				if self.locations[i,j] == 1:
					how_much_gold += 1
		return(how_much_gold)
					

class TaxMan:

	def __init__(self, tax_rate, agents, agent_count, policy, upper_rate=0.10):
		self.tax_rate = tax_rate
		self.agents = agents
		self.income = 0.0
		self.agent_count = agent_count * 1.0 #make it a real number
		self.policy = policy
		self.upper_rate = upper_rate

	def reset_zero(self):
		if (self.income < 0.00001):
			self.income = 0

	def tax_agents(self):
		if self.policy == 'flat':
			for agent in self.agents:
				remainder = agent.deduct(agent.wallet * self.tax_rate)
				self.income += agent.wallet * self.tax_rate
		if self.policy == 'upper':
			w = []
			for agent in self.agents:
				w.append(agent.wallet)
				m = median(w)
				mx = max(w)
				tq = m + ceil(0.5*(mx-m))
			for agent in self.agents:
				if agent.wallet >= tq:
					remainder = agent.deduct(agent.wallet * self.upper_rate)
					self.income += agent.wallet * self.upper_rate
				else:
					remainder = agent.deduct(agent.wallet * self.tax_rate)
					self.income += agent.wallet * self.tax_rate

	def refund_agents(self):
		fair = self.income / self.agent_count
		for agent in self.agents:
			agent.credit(fair)
			self.income -= fair
		self.reset_zero()

class Agent:

	""" Defines an agent that can move, search, and pick up gold """

	def __init__(self):
		self.location = self.draw_location()
		self.wallet = 0
		
	def draw_location(self):
		global grid_height
		global grid_width
		return(randint(0, grid_width - 1), randint(0, grid_height - 1))
	
	def search_home(self, grid):
		if grid.locations[self.location] == 0:
			return(False)
		elif grid.locations[self.location] == 1:
			return(True)
			
	def pick_up(self, grid):
		grid.locations[self.location] = 0
		self.wallet += 1
		
	def deduct(self, amount):
		""" Deducts an amount from the agents wallet and returns the amount we couldn't deduct """
		self.wallet -= amount
		amount = 0
		if (self.wallet < 0):
			amount = 0 - self.wallet
			self.wallet = 0
		return amount

	def credit(self, amount):
		""" Credit an amount to the agent's wallet and return the amount added """
		self.wallet += amount
		return amount
		
	def move(self, grid, dir):
	
		""" 1=north 2=south 3=east 4=west """
		
		global grid_width
		global grid_height
		if dir == 1 and self.location[1] < grid_height - 1:
			self.location = (self.location[0],) + (self.location[1] + 1,)
		if dir == 2 and self.location[1] > 0:
			self.location = (self.location[0],) + (self.location[1] - 1,)
		if dir == 3 and self.location[0] < grid_width - 1:
			self.location = (self.location[0] + 1,) + (self.location[1],)
		if dir == 4 and self.location[0] > 0:
			self.location = (self.location[0] - 1,) + (self.location[1],)
		else:
			self.location = self.location
			
	def search(self, grid):
		good_moves = []
		if ((self.location[0],) + (self.location[1] + 1,) in grid.locations) == True:
			good_moves.append(1)
		if ((self.location[0],) + (self.location[1] - 1,) in grid.locations) == True:
			good_moves.append(2)
		if ((self.location[0] + 1,) + (self.location[1],) in grid.locations) == True:
			good_moves.append(3)
		if ((self.location[0] - 1,) + (self.location[1],) in grid.locations) == True:
			good_moves.append(4)
		return(good_moves)
		
	def decide(self, grid):
		lg = len(self.search(grid))
		if lg == 1:
			r = 0
		elif lg == 0:
			r = randint(1, 4)
		else:
			r = randint(0, lg-1)
		return(r)
		
def reverse_lookup(d, v):
	one_id = []
	for k in d:
		if d[k] == v:
			one_id.append(k)
	return(one_id)
		
def plot_grid(agents, grid, figname):
	x_agent, y_agent = [], []
	x_gold, y_gold = [], []
	for agent in agents:
		x_agent.append(agent.location[0])
		y_agent.append(agent.location[1])
	where_gold = reverse_lookup(grid.locations, 1)
	z = zip(*where_gold)
	z0 = z[0]
	z1 = z[1]
	for i in z0:
		x_gold.append(i)
	for i in z1:
		y_gold.append(i)
	pyplot.plot(x_gold, y_gold, 'o', markerfacecolor='yellow', markersize=4)
	pyplot.plot(x_agent, y_agent, 'o', markerfacecolor='blue', markersize=8)
	pyplot.savefig(figname)
	pyplot.clf()

def run(iterations=3000, number_of_agents=300, taxrate=0.10, policy='flat', upper_rate=0.20):
	
	""" Create a list of agents. Each agents attempts to collect as much gold as 
		possible for a certain number of iterations. """

	#create our agents
	agents = [Agent() for i in range(number_of_agents)]

	#create a new default grid
	grid = Grid()
	print "Grid defined with height", grid_height, "units and width", grid_width, "units."
	print "Grid defined with", grid.how_much(), "total gold.\n\n"

	taxmaster = TaxMan(taxrate, agents, number_of_agents, policy, 0.20)

	#start our count at 0 to actually get our number of iterations
	#for example if you typed 1 iteration, it would actually result in
	# 0 iterations if we start a count at 1 (1 < 1 = false)
	count = 0
	while count < iterations:
		count += 1
		for agent in agents:
			if agent.search_home(grid) == True:
				agent.pick_up(grid)
			elif agent.search_home(grid) == False:
				agent.move(grid, agent.search(grid)[agent.decide(grid)])
		if count % 300 == 0:
			taxmaster.tax_agents()
			print "Taxed at iteration", count
			taxmaster.refund_agents()
			print "Taxes refunded at iteration", count, "\n"
		
	vals = grid.locations.values()
	stat = []
	
	for agent in agents:
		stat.append(agent.wallet)
	mean = sum(stat)/ceil(len(stat))
	
	findsd = []
	for i in stat:
		j = (i - mean)**2
		findsd.append(j)
	sd = sqrt(sum(findsd)/ceil(len(findsd)-1))
	
	w = []
	for agent in agents:
		w.append(agent.wallet)
	m = median(w)
	mn = min(w)
	mx = max(w)
	fq = m - (0.5*(m-mn))
	tq = m + (0.5*(mx-m))
	poor = 0
	super_poor = 0
	rich = 0
	super_rich = 0
	for agent in agents:
		if agent.wallet < m:
			poor += 1
		if agent.wallet < fq:
			super_poor += 1
		if agent.wallet > m:
			rich += 1
		if agent.wallet > tq:
			super_rich += 1
	
	print "\n\nAverage wallet size is", mean, "gold."
	print "Standard deviation is", sd, "gold."
	print "Taxes in the bank", taxmaster.income, "gold."
	
	bigfatwallets = []
	for agent in agents:
		bigfatwallets.append(agent.wallet)

	## calculating GINI coefficient as measurement of income disparity
	sor = sorted(bigfatwallets, reverse=True)
	n = len(sor)
	tot = []
	for i in sor:
		tot.append(float(i)*sor[int(i)])
	p = sum(tot)
	first_part = (n+1)/(n-1)
	second_part = (2)/(n*(n-1)*mean)
	gini = first_part-(second_part*p)
	print "\nThe Gini coefficient is", gini, "\n"
		
	print "Total wealth is", sum(bigfatwallets), "gold."
	print "There are", poor, "agents below the median."
	print "There are", rich, "agents above the median."
	print "There are", super_poor, "agents below the first quartile."
	print "There are", super_rich, "agents above the third quartile."

	return(bigfatwallets)
		
def hist(bfw, figname):
	pyplot.hist(bfw)
	pyplot.savefig(figname)
	pyplot.clf()
				
def single_run(grid=g):
	for agent in a:
		if agent.search_home(grid) == True:
			agent.pick_up(grid)
		elif agent.search_home(grid) == False:
			agent.move(grid, agent.search(grid)[agent.decide(grid)])
	w = []
	for i in a:
		w.append(i.wallet)
	m = median(w)
	mx = max(w)
	tq = m + ceil(0.5*(mx-m))
	print m, mx, tq
		
def main(type='flat',main_rate=0.00,upper_rate=0.20):
	wallet = run(3000,300,main_rate,type,upper_rate)
	hist(wallet, 'test')

#if __name__ == '__main__':
#		main()
