import os
import argparse
import json
from test_single_simu import test_single_simu
from test_start_stop import test_start_and_stop
import numpy as np
import matplotlib.pyplot as plt

def convert_int64(obj):
    if isinstance(obj, dict):
        return {k: convert_int64(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_int64(v) for v in obj]
    elif isinstance(obj, np.int64):
        return int(obj)
    else:
        return obj

def lighten_color(color, amount=0.5):
    """
    Lightens the given color by multiplying (1-luminosity) by the given amount.
    Input can be matplotlib color string, hex string, or RGB tuple.

    Parameters:
    - color: The color to lighten
    - amount: The amount to lighten the color. 0 will be the original color, 1 will be white.

    Returns:
    - Lightened color
    """
    import matplotlib.colors as mc
    import colorsys
    try:
        c = mc.cnames[color]
    except:
        c = color
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    return colorsys.hls_to_rgb(c[0], 1 - amount * (1 - c[1]), c[2])

def create_combined_boxplots(output_dir):
    # Load the data from the JSON file
    with open(os.path.join(output_dir, 'quantitative_test.json'), 'r') as f:
        data = json.load(f)

    # Extract the data for each category
    alive = data['Alive']
    necrotic = data['Necrotic']
    apoptotic = data['Apoptotic']
    alive_s_s = data['Alive_Start_Stop']
    necrotic_s_s = data['Necrotic_Start_Stop']
    apoptotic_s_s = data['Apoptotic_Start_Stop']

    # Define the categories for the boxplots
    categories = ['Alive', 'Necrotic', 'Apoptotic']
    letters = ['a', 'b', 'c']
    # Get a color map to use different colors for each category
    cmap = plt.get_cmap('Set1')
    colors = [cmap(i) for i in range(len(categories))]

    # Define the x-axis values (time steps in minutes)
    x_values = [150, 300, 450, 600, 750, 900, 1050, 1200, 1350, 1440]

    # Create a figure and a set of subplots (one for each category)
    fig, axs = plt.subplots(3, 1, figsize=(5, 8))  # Reduced the size
    # Set the main title of the figure
    fig.suptitle('Comparison between Normal and Start-Stop Simulation', fontsize=10)  # Reduced font size

    # Define the x-axis positions as sequential integer values
    x_positions = list(range(len(x_values)))

    for i, ax in enumerate(axs):
        # Get the current category and the corresponding data
        category = categories[i]
        data_normal = eval(category.lower())
        data_s_s = eval(category.lower() + '_s_s')

        # Prepare the data to be plotted for both normal and start-stop simulations
        data_to_plot_normal = [data_normal[j] for j in range(10)]
        data_to_plot_s_s = [data_s_s[j] for j in range(10)]

        # Store the boxplot elements to use in the legend
        boxplot_elements = []

        for j in range(10):
            # Plot the boxplots using the integer positions on the x-axis
            # Adjust the positions to place the boxplots side by side
            bp_normal = ax.boxplot(data_to_plot_normal[j], positions=[x_positions[j] - 0.2], widths=0.3, patch_artist=True, boxprops=dict(facecolor=colors[i]))
            lighter_color = lighten_color(colors[i], amount=0.3)
            bp_s_s = ax.boxplot(data_to_plot_s_s[j], positions=[x_positions[j] + 0.2], widths=0.3, patch_artist=True, boxprops=dict(facecolor=lighter_color))
            
            # Collect boxplot elements for legend
            if j == 0:  # Only need to add the first boxplot to the legend
                boxplot_elements.append(bp_normal["boxes"][0])
                boxplot_elements.append(bp_s_s["boxes"][0])

        # Set the x-axis labels mapping the integer positions to the corresponding time steps
        ax.set_xticks(x_positions)
        ax.set_xticklabels(x_values)
        ax.set_xlabel('Time steps (minutes)', fontsize=10)  # Reduced font size
        ax.set_ylabel(f'{category} Cells', fontsize=10)  # Reduced font size
        # Adjust the font size for the axis tick labels
        ax.tick_params(axis='x', labelsize=8)  # Reduced font size
        ax.tick_params(axis='y', labelsize=8)  # Reduced font size
        # Set the title for each subplot
        ax.set_title(f'{letters[i]}) {category} Cells', fontsize=10)  # Reduced font size

        # Set the legend location based on the category
        if category == 'Necrotic':
            loc = 'lower right'
        else:
            loc = 'upper right'
        ax.legend(boxplot_elements, ['Normal', 'Start-Stop'], loc=loc, fontsize=8)  # Reduced font size

    # Adjust the layout to make room for the main title
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    # Save the figure to the specified output directory
    plt.savefig(os.path.join(output_dir, 'combined_cells_boxplot.pdf'))
    # Close the figure to free up memory
    plt.close()
    
def quantitative_test(output_dir):
    dir = os.getcwd()
    os.chdir('..')

    num_simu = 50

    step = 150

    two_D = True

    alive, apoptotic, necrotic, durations = test_single_simu(num_simu, step, two_D)

    alive_s_s, apoptotic_s_s, necrotic_s_s, durations_ss = test_start_and_stop(num_simu, step, two_D)

    data = {
        'Alive': alive,
        'Apoptotic': apoptotic,
        'Necrotic': necrotic,
        'Durations': durations,
        'Alive_Start_Stop': alive_s_s,
        'Apoptotic_Start_Stop': apoptotic_s_s,
        'Necrotic_Start_Stop': necrotic_s_s,
        'Durations_Start_Stop': durations_ss
    }
    
    data = convert_int64(data)
    # save the data as json
    with open(os.path.join(output_dir, 'quantitative_test.json'), 'w') as f:
        json.dump(data, f, indent = 4)
    



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run qualitative test with specified output directory.')
    parser.add_argument('output_dir', type=str, help='The output directory')

    args = parser.parse_args()

    quantitative_test(args.output_dir)

    create_combined_boxplots(args.output_dir)
