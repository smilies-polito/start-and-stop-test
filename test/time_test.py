import os
import matplotlib.pyplot as plt
from test_single_simu import test_single_simu
from test_start_stop import test_start_and_stop
from helpers.plots.create_boxplots import create_boxplots

dir = os.getcwd()

num_simu = 30

step = 150

two_D = False

os.chdir(dir)

alive, apoptotic, necrotic, durations = test_single_simu(num_simu, step, two_D)

os.chdir(dir)

alive_s_s, apoptotic_s_s, necrotic_s_s, durations_s_s = test_start_and_stop(num_simu, step, two_D)

data_to_plot = [durations, durations_s_s]

# Create a new figure and axis
fig, ax = plt.subplots()

# Define positions for boxplots along the x-axis
positions = range(len(data_to_plot) + 1)[1:]

# Plot the boxplots
ax.boxplot(data_to_plot, positions=positions)

# Set labels for x and y axes and title
ax.set_xlabel('Simulation')
ax.set_ylabel('Duration [s]')
ax.set_title('Box Plot durations 3D')

# Set the x-axis tick positions and labels
ax.set_xticks(positions)
ax.set_xticklabels(['single simulations', 'start&stop'])

image_dir = os.path.join(dir, 'images/duration')
print(image_dir)

filename = 'durations_3D.png'

# Save the box plot as an image
plt.savefig(os.path.join(image_dir, filename))

# Close the plot to free up memory
plt.close()



