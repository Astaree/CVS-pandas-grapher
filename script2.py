# This script processes CSV files containing temperature data for multiple samples,
# calculates the average temperature and cooling rate for each sample, and saves the
# data to an Excel file. It then generates a multi-plot figure showing the temperature
# and cooling rate over time for each sample, and displays the figure.
# The path to the directory containing the CSV files should be passed as a command-line
# argument when running the script.

import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from openpyxl import load_workbook

def process_files(path):
    all_data = [] # create a list to store all dataframes
    with pd.ExcelWriter("./cooling_data.xlsx", engine='xlsxwriter') as writer:
        for filename in os.listdir(path): # loop through all files in the specified directory
            if filename.endswith(".csv"):
                data = pd.read_csv(os.path.join(path, filename), names=['Time', 'Temperature_1', 'Temperature_2', 'Temperature_3'], header=None, delimiter=';') # read data from the CSV file, setting column names and specifying no header
                data["File"] = filename # add a column with the filename
                all_data.append(data) # append the data to the overall list of dataframes
                data["Avg_Temp"] = data[["Temperature_1", "Temperature_2", "Temperature_3"]].mean(axis=1)
                data["Cooling_Rate"] = data["Avg_Temp"].diff() / data["Time"].diff()
                data.to_excel(writer, sheet_name=filename.split('.')[0])

        all_data = pd.concat(all_data, ignore_index=True)
        # Create a 3x1 grid of subplots
        fig = plt.figure(figsize=(6, 6))
        gs = GridSpec(3, 1)

        files = all_data['File'].unique()
        axs = [fig.add_subplot(gs[i]) for i in range(3)]

        for i, file in enumerate(files):
            data = all_data[all_data["File"] == file]
            axs[i].plot(data["Time"], data["Avg_Temp"],label = 'Temperature over time')
            axs[i].set_title(f"Cooling of Sample: {file}")
            axs[i].set_xlabel("Time (s)")
            axs[i].set_ylabel("Temperature (C)")
            ax2 = axs[i].twinx() 
            ax2.plot(data["Time"], data["Cooling_Rate"], 'r',label = 'Cooling rate over time')
            ax2.set_ylabel("Cooling rate (C/s)")
            ax2.invert_yaxis()

        handles, labels = axs[0].get_legend_handles_labels()
        handles2, labels2 = ax2.get_legend_handles_labels()
        handles += handles2
        labels += labels2

        leg = fig.legend(handles, labels, bbox_to_anchor=(0, 0, 1, 0.1), loc=3, ncol=4, mode="expand", borderaxespad=0)
        gs.tight_layout(fig, rect=[0.05, 0.05, 0.95, 0.95])
        plt.show() # display the plot


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="The path to the directory containing the CSV files")
    args = parser.parse_args()
    process_files(args.path)
