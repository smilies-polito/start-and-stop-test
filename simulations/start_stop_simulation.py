import sys
import os
import math
sys.path.append('../')
from interface.interface import interface

def start_stop_simu(step, two_D):
    os.chdir('..')
    root_dir = os.getcwd()
    json_file_path = os.path.join(root_dir, 'helpers/simulation_parameters/simulation_parameters.json')

    # define interface object
    my_interface = interface(root_dir, json_file_path, two_D)
    duration = my_interface.parameter_dict['max_time']['value']
    num_iter = math.ceil(duration/step)

    # define current time
    current_time = 0

    # define usefull lists
    step_alive = []
    step_apoptotic = []
    step_necrotic = []
    time_steps = []

    # Execute the simulation with new parameters
    for iteration in range(num_iter):

        # here we will put the function that calls the reinforcement learning and updates the parameters in the correct way

        if iteration == 0:
            my_interface.parameter_dict['read_init']['value'] = 'false'
            my_interface.parameter_dict['max_time']['value'] = step
            current_time += step
        else:
            my_interface.parameter_dict['seed_tnf']['value'] = 'false'
            my_interface.parameter_dict['start_stop']['value'] = 'true'
            if (current_time + step) < duration:
                my_interface.parameter_dict['read_init']['value'] = 'true'
                my_interface.parameter_dict['if_start_inj']['value'] = 'true'
                current_time += step
                my_interface.parameter_dict['max_time']['value'] = current_time
            else:
                my_interface.parameter_dict['read_init']['value'] = 'true'
                my_interface.parameter_dict['if_start_inj']['value'] = 'true'
                current_time = duration
                my_interface.parameter_dict['max_time']['value'] = duration
                


        # Call update parameters function
        my_interface.update_parameters(iteration)


        # execute simulation
        output_folder = my_interface.execute_simulation(iteration)

    # Count alive cells for iteration and plot
    time_steps_flag, step_alive_flag, step_apoptotic_flag, step_necrotic_flag, pos = my_interface.alive_cells()

    # Execute plot
    my_interface.plot(time_steps_flag, step_alive_flag, step_necrotic_flag, step_apoptotic_flag, pos)

    # evaluate resistance
    percentage_of_resistant, stable_cells = my_interface.resistance_detection(step_alive_flag[-1])
    
    return time_steps_flag, step_alive_flag, step_necrotic_flag, step_apoptotic_flag, percentage_of_resistant, stable_cells

if __name__ == "__main__":
    step = 600
    two_D = True
    time_steps, step_alive, step_necrotic, step_apoptotic, percentage_of_resistant, stable_cells = start_stop_simu(step, two_D)
    print(percentage_of_resistant)
    print(stable_cells)