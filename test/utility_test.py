import sys
import argparse
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
sys.path.append('../')
from interface.interface import interface
from simulations.single_simulation import single_simu

def convert_int64(obj):
    if isinstance(obj, dict):
        return {k: convert_int64(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_int64(v) for v in obj]
    elif isinstance(obj, np.int64):
        return int(obj)
    else:
        return obj

def create_combined_stackplot(output_dir):
    # Leggi il file JSON
    with open(f"{output_dir}/qualitative_test.json", 'r') as file:
        data = json.load(file)
    
    # Estrai i dati dal file JSON
    time_steps_tot = data['time_steps_tot']
    step_alive_tot = data['step_alive_tot']
    step_necrotic_tot = data['step_necrotic_tot']
    step_apoptotic_tot = data['step_apoptotic_tot']
    pos_tot = data['pos_tot']
    stop_times = data['stop_times']
    resistant_cells_vec = data['resistant_cells_vec']

    # Usa la colormap Set1 per i colori
    cmap = plt.get_cmap('Set1')
    color_alive = cmap(4)
    color_necrotic = cmap(1)
    color_apoptotic = cmap(2)
    color_resistant = cmap(3)  # Utilizzato solo se resistance è True

    # Crea la figura per contenere i subplot
    fig, axs = plt.subplots(4, 1, figsize=(6, 10))  # Dimensioni modificate per adattare i subplot

    # Definisci i titoli per ogni subplot
    titles = ['Continuous Simulation Resistance', 'Start-Stop Simulation Resistance', 
              'Continuous Simulation Alive Cells', 'Start-Stop Simulation Alive Cells']
    letters = ['a', 'b', 'c', 'd']  # Lettere per ogni subplot

    # Loop attraverso ogni subplot e plotta i dati
    for i, ax in enumerate(axs.flat):
        if stop_times[i] is not None:
            resistant_cells_vec[i].pop(round(stop_times[i]/30))
            ax.axvline(x=stop_times[i], color='r', linestyle='--', label='Stop Time')
        ax.stackplot(time_steps_tot[i], list(np.array(step_alive_tot[i]) - np.array(resistant_cells_vec[i])), 
                     resistant_cells_vec[i], step_necrotic_tot[i], step_apoptotic_tot[i], 
                     colors=[color_alive, color_resistant, color_necrotic, color_apoptotic], 
                     labels=['Alive Cells', 'Resistant Cells', 'Necrotic Cells', 'Apoptotic Cells'])
            
        # Imposta il titolo e regola il layout
        ax.set_title(f"{letters[i]}) {titles[i]}", fontsize=10, fontweight='bold')  # Includi la lettera nel titolo
        ax.set_xlabel('Time (min)', fontsize=10)
        ax.set_ylabel('Number of Cells', fontsize=10)
        ax.set_xticks([0, 150, 300, 450, 600, 750, 900, 1050, 1200, 1350])
        ax.tick_params(axis='both', which='major', labelsize=10)
        ax.legend(fontsize=8)
        ax.grid(True)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(f"{output_dir}/combined_stackplot.pdf")
    plt.close()
    print(stop_times)


def qualitative_test(output_dir):
    # Set the root dir
    os.chdir('..')
    root_dir = os.getcwd()

    # set the 2 D
    two_D = True
    # ----------------------------------------#
    # CONTINUOUS SIMULATION ALIVE CELLS
    # Read the json file to set the parameters, made this way to reuse the interface
    json_file_path = 'helpers/simulation_parameters/simulation_parameters.json'
    with open(json_file_path, 'r') as file:
        parameter_dict = json.load(file)

    # update parameters according to the current ideal simulation
    parameter_dict['auto_stop']['value'] = 'false'
    parameter_dict['start_stop']['value'] = 'false'
    parameter_dict['read_init']['value'] = 'false'
    parameter_dict['auto_stop_resistance']['value'] = 'false'
    parameter_dict['tnf_pulse_concentration']['value'] = 0.005
    parameter_dict['tnf_pulse_duration']['value'] = 10
    parameter_dict['tnf_pulse_period']['value'] = 600
    parameter_dict['if_start_inj']['value'] = 'true'

    #update the json file
    with open(json_file_path, 'w') as file:
        json.dump(parameter_dict, file, indent=4)

    #execute the first simulation with initial parameters
    time_steps_cont_alive, step_alive_cont_alive, step_necrotic_cont_alive, step_apoptotic_cont_alive, pos_cont_alive, percentage_of_resistant_cont_alive, stable_cells_cont_alive = single_simu(two_D, resistance=True)
    resistance_cont_alive = pd.read_csv('../model/output/resistant_cells.txt', header=None).values.flatten().tolist()
    #move the plot in the output folder

    # ----------------------------------------#
    # START STOP SIMULATION ALIVE CELLS
    # update the parameters for the second simulation
    os.chdir('..')
    parameter_dict['auto_stop']['value'] = 'true'
    parameter_dict['auto_stop_resistance']['value'] = 'false'

    #update the json file
    with open(json_file_path, 'w') as file:
        json.dump(parameter_dict, file, indent=4)

    #run the first simulation until it auto stops
    json_file_path = os.path.join(root_dir, json_file_path)

    # define interface object
    my_interface = interface(root_dir, json_file_path, two_D)

    # update_parameters
    iteration = 0

    my_interface.update_parameters(iteration)

    # Execute the simulation with new parameters

    output_folder = my_interface.execute_simulation(iteration)

    time_steps, step_alive, step_apoptotic, step_necrotic, pos = my_interface.alive_cells()

    # Set parameters for the plot
    stop_time_ss_alive = time_steps[-1]

    # update the parameters
    parameter_dict['start_stop']['value'] = 'true'
    parameter_dict['tnf_pulse_concentration']['value'] = 0.005
    parameter_dict['tnf_pulse_duration']['value'] = 10
    parameter_dict['tnf_pulse_period']['value'] = 150

    #update the json file
    with open(json_file_path, 'w') as file:
        json.dump(parameter_dict, file, indent=4)

    #run the second simulation until the end
    # define interface object
    my_interface = interface(root_dir, json_file_path, two_D)

    # update_parameters
    iteration = 1

    my_interface.update_parameters(iteration)

    # Execute the simulation with new parameters

    output_folder = my_interface.execute_simulation(iteration)

    # Count alive cells for iteration and plot
    time_steps_ss_alive, step_alive_ss_alive, step_apoptotic_ss_alive, step_necrotic_ss_alive, pos_ss_alive = my_interface.alive_cells()
    resistance_ss_alive = pd.read_csv('../model/output/resistant_cells.txt', header=None).values.flatten().tolist()

    #print(len(time_steps))

    # Execute plot
    my_interface.plot(time_steps_ss_alive, step_alive_ss_alive, step_necrotic_ss_alive, step_apoptotic_ss_alive, pos_ss_alive, resistance=True, stop_time=stop_time_ss_alive, stop=True)

    # ----------------------------------------#
    # CONTINUOUS SIMULATION RESISTANCE
    os.chdir('..')
    # Read the json file to set the parameters, made this way to reuse the interface
    json_file_path = 'helpers/simulation_parameters/simulation_parameters.json'
    with open(json_file_path, 'r') as file:
        parameter_dict = json.load(file)

    # update parameters according to the current ideal simulation
    parameter_dict['auto_stop']['value'] = 'false'
    parameter_dict['start_stop']['value'] = 'false'
    parameter_dict['read_init']['value'] = 'false'
    parameter_dict['tnf_pulse_concentration']['value'] = 0.1
    parameter_dict['tnf_pulse_duration']['value'] = 10000000000
    parameter_dict['tnf_pulse_period']['value'] = 100000000000
    parameter_dict['if_start_inj']['value'] = 'true'

    #update the json file
    with open(json_file_path, 'w') as file:
        json.dump(parameter_dict, file, indent=4)

    #execute the first simulation with initial parameters
    time_steps_cont_res, step_alive_cont_res, step_necrotic_cont_res, step_apoptotic_cont_res, pos_cont_res, percentage_of_resistant_cont_res, stable_cells_cont_res = single_simu(two_D, resistance=True)
    resistance_cont_res = pd.read_csv('../model/output/resistant_cells.txt', header=None).values.flatten().tolist()

    # ----------------------------------------#
    # START STOP SIMULATION RESISTANCE
    # update the parameters for the second simulation
    # Set the root dir
    os.chdir('..')
    root_dir = os.getcwd()

    # set the 2 D
    two_D = True

    # Read the json file to set the parameters, made this way to reuse the interface
    json_file_path = 'helpers/simulation_parameters/simulation_parameters.json'
    with open(json_file_path, 'r') as file:
        parameter_dict = json.load(file)

    # update parameters according to the current ideal simulation
    parameter_dict['auto_stop']['value'] = 'true'
    parameter_dict['auto_stop_resistance']['value'] = 'true'

    #update the json file
    with open(json_file_path, 'w') as file:
        json.dump(parameter_dict, file, indent=4)

    #run the first simulation until it auto stops
    json_file_path = os.path.join(root_dir, json_file_path)

    # define interface object
    my_interface = interface(root_dir, json_file_path, two_D)

    # update_parameters
    iteration = 0

    my_interface.update_parameters(iteration)

    # Execute the simulation with new parameters

    output_folder = my_interface.execute_simulation(iteration)

    time_steps, step_alive, step_apoptotic, step_necrotic, pos = my_interface.alive_cells()

    # Set parameters for the plot
    stop_time_ss_res = time_steps[-1]

    # update the parameters
    #parameter_dict['auto_stop']['value'] = 'false'
    parameter_dict['start_stop']['value'] = 'true'
    parameter_dict['auto_stop_resistance']['value'] = 'true'
    parameter_dict['tnf_pulse_concentration']['value'] = 0.005
    parameter_dict['tnf_pulse_duration']['value'] = 10
    parameter_dict['tnf_pulse_period']['value'] = 150

    #update the json file
    with open(json_file_path, 'w') as file:
        json.dump(parameter_dict, file, indent=4)

    #run the second simulation until the end
    # define interface object
    my_interface = interface(root_dir, json_file_path, two_D)

    # update_parameters
    iteration = 1

    my_interface.update_parameters(iteration)

    # Execute the simulation with new parameters

    output_folder = my_interface.execute_simulation(iteration)

    # Count alive cells for iteration and plot
    time_steps_ss_res, step_alive_ss_res, step_apoptotic_ss_res, step_necrotic_ss_res, pos_ss_res = my_interface.alive_cells()
    resistance_ss_res = pd.read_csv('../model/output/resistant_cells.txt', header=None).values.flatten().tolist()

    # Execute plot
    my_interface.plot(time_steps_ss_res, step_alive_ss_res, step_necrotic_ss_res, step_apoptotic_ss_res, pos_ss_res, resistance=True, stop_time=stop_time_ss_res, stop=True)

    # create a variable to handle all the plots

    data = {
        "time_steps_tot": [list(time_steps_cont_res), list(time_steps_ss_res), list(time_steps_cont_alive), list(time_steps_ss_alive)],
        "step_alive_tot": [list(step_alive_cont_res), list(step_alive_ss_res), list(step_alive_cont_alive), list(step_alive_ss_alive)],
        "step_necrotic_tot": [list(step_necrotic_cont_res), list(step_necrotic_ss_res), list(step_necrotic_cont_alive), list(step_necrotic_ss_alive)],
        "step_apoptotic_tot": [list(step_apoptotic_cont_res), list(step_apoptotic_ss_res), list(step_apoptotic_cont_alive), list(step_apoptotic_ss_alive)],
        "pos_tot": [pos_cont_res, pos_ss_res, pos_cont_alive, pos_ss_alive],
        "stop_times": [None, stop_time_ss_res, None, stop_time_ss_alive],
        "resistant_cells_vec": [resistance_cont_res, resistance_ss_res, resistance_cont_alive, resistance_ss_alive]
    }
    data = convert_int64(data)

    
    # save the file
    with open(f"{output_dir}/qualitative_test.json", 'w') as file:
        json.dump(data, file, indent=4)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run qualitative test with specified output directory.')
    parser.add_argument('output_dir', type=str, help='The output directory')

    args = parser.parse_args()

    qualitative_test(args.output_dir)

    create_combined_stackplot(args.output_dir)
