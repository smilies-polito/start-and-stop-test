import matplotlib.pyplot as plt
import os

def create_boxplots(data_to_plot, ylabel, current_dir, type):
    # Create a new figure and axis
    fig, ax = plt.subplots()

    # Define positions for boxplots along the x-axis
    positions = range(len(data_to_plot) + 1)[1:]

    # Plot the boxplots
    ax.boxplot(data_to_plot, positions=positions)

    # Set labels for x and y axes and title
    ax.set_xlabel('Stops')
    ax.set_ylabel(ylabel)
    ax.set_title(f'Box Plot {type} Simulation')

    # Set the x-axis tick positions and labels
    ax.set_xticks(positions)
    ax.set_xticklabels(['150', '300', '450', '600', '750', '900', '1050', '1200', '1350', '1440'])

    # Save the box plot as an image
    plt.savefig(os.path.join(current_dir, f'{ylabel.lower().replace(" ", "_")}.pdf'))

    # Close the plot to free up memory
    plt.close()

