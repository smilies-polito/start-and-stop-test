import sys
import os
import time
sys.path.append('../')
from interface.interface import interface

os.chdir('..')
root_dir = os.getcwd()
json_file_path = os.path.join(root_dir, 'helpers/simulation_parameters/simulation_parameters.json')

output_folder = os.path.join(root_dir, 'model/output')

# define interface object
my_interface = interface(root_dir, json_file_path, True)

time_steps, step_alive, step_apoptotic, step_necrotic, pos = my_interface.alive_cells()

my_interface.plot(time_steps, step_alive, step_necrotic, step_apoptotic, pos)

percentage_of_resistant, stable_cells = my_interface.resistance_detection(step_alive[-1])

print(stable_cells)