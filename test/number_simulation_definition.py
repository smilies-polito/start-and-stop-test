import os
import numpy as np
from test_single_simu import test_single_simu

# we want to have the 95% of probability of the mean to be between estimated mean +- 10 cells = estimated mean +- 1.96*sem 
range = 10
sem = range/1.96

dir = os.getcwd()

num_simu = 100

step = 600

two_D = True

os.chdir(dir)

alive, apoptotic, necrotic, durations = test_single_simu(num_simu, step, two_D)

std = np.std(alive[2])

sqrtn = std/sem
n = sqrtn**2

print(f'the number of simulations required is {n}')