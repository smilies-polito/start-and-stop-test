import sys
import os
sys.path.append('../')
from interface.interface import interface

def single_simu(two_D, resistance=False):
    root_dir = os.getcwd()
    json_file_path = os.path.join(root_dir, 'helpers/simulation_parameters/simulation_parameters.json')

    # define interface object
    my_interface = interface(root_dir, json_file_path, two_D)

    # update_parameters
    iteration = 0
    
    my_interface.update_parameters(iteration)

    # Execute the simulation with new parameters

    output_folder = my_interface.execute_simulation(iteration)

    # Count alive cells for iteration and plot
    time_steps, step_alive, step_apoptotic, step_necrotic, pos = my_interface.alive_cells()

    #print(len(time_steps))
    # Execute plot
    my_interface.plot(time_steps, step_alive, step_necrotic, step_apoptotic, pos, resistance=resistance)

    # evaluate resistance
    percentage_of_resistant, stable_cells = my_interface.resistance_detection(step_alive[-1])
    
    return time_steps, step_alive, step_necrotic, step_apoptotic, pos, percentage_of_resistant, stable_cells

if __name__ == "__main__":

    os.chdir('..')
    two_D = True
    time_steps, step_alive, step_necrotic, step_apoptotic, pos, percentage_of_resistant, stable_cells  = single_simu(two_D)
    print(percentage_of_resistant)
    print(stable_cells)