import os
import subprocess
import xml.etree.ElementTree as ET
import shutil
import json
import sys
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from pctk import multicellds
sys.path.append('../')


class interface:
    def __init__(self, root_dir, json_file_path, two_D):

        # define the directory
        self.root_dir = root_dir
        self.PhysiBoSS_dir = os.path.join(root_dir, 'model')
        self.two_D = two_D

        #define the parameter dict
        self.json_file_path = json_file_path
        with open(json_file_path, 'r') as file:
            self.parameter_dict = json.load(file)
        
        if self.two_D:
            self.parameter_dict['z_min']['value'] = -10
            self.parameter_dict['z_max']['value'] = 10
            self.parameter_dict['use_2D']['value'] = 'true'
        else:
            self.parameter_dict['z_min']['value'] = -500
            self.parameter_dict['z_max']['value'] = 500
            self.parameter_dict['use_2D']['value'] = 'false'

        self.output_folder = os.path.join(self.PhysiBoSS_dir, 'output')

    def update_parameters(self, iteration):
        
        # File path for the physicell settings
        if iteration == 0:
            physicell_setting_file = os.path.join(self.root_dir, 'model/sample_projects_intracellular/boolean/spheroid_tnf_model/config/PhysiCell_settings.xml')
        else:
            physicell_setting_file = os.path.join(self.root_dir, 'model/config/PhysiCell_settings.xml')

        # Path for the directory with the saving of old simulation
        old_simu_path = os.path.join(self.root_dir, 'model/starting_file_trial')
        
        # Upload XML file
        tree = ET.parse(physicell_setting_file)
        root = tree.getroot()
        
        # Extract list of parameters to update
        parameters = list(self.parameter_dict.keys())
        
        for param in parameters:
            # Find parameter tags
            tags = self.parameter_dict[param]['path'].split('/')
            
            # Find tag to modify
            element = root
            for tag in tags:
                if element is not None:
                    if tag == 'variable' and 'name' in self.parameter_dict[param]:
                        # Find the variable with the specific name
                        found = False
                        for var in element.findall(tag):
                            if var.attrib['name'] == self.parameter_dict[param]['name']:
                                element = var
                                found = True
                                break
                        if not found:
                            element = None
                            break
                    elif tag != 'variable':
                        element = element.find(tag)
                
            #Update the value
            new_value = str(self.parameter_dict[param]['value'])

            if element is not None:
                element.text = new_value

            # Save XML file
            tree.write(physicell_setting_file)
            
        return 'Settings updated succesfully!'
    
    def execute_simulation(self, iteration):
        # Change current working directory
        os.chdir(self.PhysiBoSS_dir)
        
        # Need to be updated but for now let's mantain this
        executable_file = 'spheroid_TNF_model'

        if iteration == 0:

            # Recreate output folder
            first_make_command = ["make", 'data-cleanup']
            subprocess.run(first_make_command, check=True)

            reset_make_command = ["make", 'reset']
            subprocess.run(reset_make_command, check=True)
            
            clean_make_command = ["make", 'clean']
            subprocess.run(clean_make_command, check=True)

            make_command = ["make", "physiboss-tnf-model"]
            subprocess.run(make_command, check=True)
        
            make_command = ["make"]
            subprocess.run(make_command, check=True)
        
        # Run the simulation
        execute_command = ["./" + executable_file]
        subprocess.run(execute_command, check=True) 
        
        return self.output_folder
    
    def alive_cells(self):
        # Creating a MCDS reader
        reader = multicellds.MultiCellDS(output_folder=self.output_folder)

        # Creating an iterator to load a cell DataFrame for each stored simulation time step
        df_iterator = reader.cells_as_frames_iterator()

        step_alive = []
        step_apoptotic = []
        step_necrotic = []
        time_steps = []
        print("\n")

        for (t, df_cells) in df_iterator:
            alive = (df_cells.current_phase==14).sum()
            apoptotic = (df_cells.current_phase==100).sum()
            necrotic = (df_cells.current_phase==101).sum()
            step_alive.append(alive)
            step_apoptotic.append(apoptotic)
            step_necrotic.append(necrotic)
            time_steps.append(t)
            print(f"Total alive {alive}, necrotic {necrotic} and apoptotic {apoptotic} cells at time {t}")
        
        pos = (df_cells[['x_position', 'y_position', 'z_position', 'current_phase']].values).tolist()

        
        return time_steps, step_alive, step_apoptotic, step_necrotic, pos


    def plot(self, time_steps, step_alive, step_necrotic, step_apoptotic, pos, resistance=False, stop_time=None, stop=False):
        # Use Set1 colormap for colors
        cmap = plt.get_cmap('Set1')
        color_alive = cmap(0)
        color_necrotic = cmap(1)
        color_apoptotic = cmap(2)
        color_resistant = cmap(3)  # Only used if resistance is True

        # Plotting the data
        fig, ax = plt.subplots(figsize=(10, 6))

        if resistance:
            df = pd.read_csv('../model/output/resistant_cells.txt', header=None)
            resistant_cells = df.values.flatten().tolist()
            if stop:
                resistant_cells.pop(round(stop_time/30))

            # Create stackplot with resistance
            ax.stackplot(time_steps, list(np.array(step_alive)-np.array(resistant_cells)), resistant_cells, step_necrotic, step_apoptotic, colors=[color_alive, color_resistant, color_necrotic, color_apoptotic], labels=['Alive Cells', 'Resistant Cells', 'Necrotic Cells', 'Apoptotic Cells'])
        else:
            # Create stackplot without resistance
            ax.stackplot(time_steps, step_alive, step_necrotic, step_apoptotic, colors=[color_alive, color_necrotic, color_apoptotic], labels=['Alive Cells', 'Necrotic Cells', 'Apoptotic Cells'])

        if stop_time is not None:
            ax.axvline(x=stop_time, color='black', linestyle='--', label='Stop Time')

        # Increase font size and use Set1 colormap
        ax.set_xlabel('Time (min)', fontsize=14)
        ax.set_ylabel('Number of Cells', fontsize=14)
        ax.set_title('Cell Population over Time', fontsize=16)
        ax.set_xticks([0, 150, 300, 450, 600, 750, 900, 1050, 1200, 1350])
        ax.tick_params(axis='both', which='major', labelsize=15)
        ax.legend(fontsize=15)
        ax.grid(True)

        plt.savefig(os.path.join(self.output_folder, 'cell_population_over_time.pdf'))
    
    def resistance_detection(self, alive_cells):

        
        stable_states = ['TNF TNFR RIP1 RIP1ub RIP1K IKK NFkB BCL2 ATP cIAP XIAP cFLIP Survival',
                        'FASL TNF TNFR RIP1 RIP1ub RIP1K IKK NFkB BCL2 ATP cIAP XIAP cFLIP Survival',
                        'TNF TNFR DISC-TNF FADD RIP1 RIP1ub RIP1K IKK NFkB BCL2 ATP cIAP XIAP cFLIP Survival',
                        'FASL DISC-FAS FADD RIP1 RIP1ub RIP1K IKK NFkB BCL2 ATP cIAP XIAP cFLIP Survival',
                        'FASL TNF TNFR DISC-TNF DISC-TNF FADD RIP1 RIP1ub RIP1K IKK NFkB BCL2 ATP cIAP XIAP cFLIP Survival']
        for i in range(len(stable_states)):
            stable_states[i] = stable_states[i].split(' ')

        # read the bool_data.txt file
        filename = os.path.join(self.PhysiBoSS_dir, 'starting_file_trial/bool_data.txt')
        command = ["awk", "{print}", filename]
        result = subprocess.run(command, capture_output=True, text=True)
        lines = result.stdout.split('\n')[:-1]

        counter_stable = 0
        for raw_line in lines:
            raw_line = raw_line.split(' ')
            line = []
            for i in range(len(raw_line)-1):
                flag = raw_line[i].replace(";", "").split('=')
                node = flag[0]
                value = flag[1]

                if value == '1':
                    line.append(node)

            for state in stable_states:
                if set(state).issubset(set(line)):
                    counter_stable += 1
                    break  # exit the inner loop if a match is found

        percentage_of_resistant = counter_stable/alive_cells
        
        return percentage_of_resistant, counter_stable



