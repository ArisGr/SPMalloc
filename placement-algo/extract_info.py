import re
from pathlib import Path
import csv

# Function to get columns from the pcm-memory.csv files. We get the Write BW values for optane and dram.
def extract_column(file_path, index):
    try:
        # Open the CSV file
        with open(file_path, mode='r') as file:
            csv_reader = csv.reader(file)

            # Initialize a list to hold the values from desired column 
            column_data = []

            # Loop through each row in the CSV file
            for row in csv_reader:
                try:
                    if len(row) > index-1:
                        # Extract the value from column x (index x-1), ignore the first two descriptors (those are string element which are not useful)
                        value = float(row[index-1].strip())
                        column_data.append(value)  
                except (ValueError, IndexError):
                    continue
            return column_data

    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Convenience function to extract both optane and dram write columns
def extract_csv(optane_path, dram_path):
    # optane write bw values are column 72 in the csv file
    optane_writes = extract_column(optane_path, 72)
    # dram write bw values are column 70 in the csv file
    dram_writes = extract_column(dram_path, 70)
    return optane_writes, dram_writes





# Function to extract allocated_bytes and active_objects from the logfile of SPMalloc.
def extract_txt(log_path):
    allocated_bytes = [0]
    objects_alive = [0]

    pattern = re.compile(r"Allocated: (\d+) bytes \(second [\d.]+\) \(objects alive = (\d+)\)")

    with open(log_path, 'r') as file:
        for line in file:
            # Check if the line matches the expected format
            match = pattern.match(line)
            if match:
                # Extract allocated bytes and objects alive
                allocated_bytes.append(int(match.group(1)))
                objects_alive.append(int(match.group(2)))

    return allocated_bytes, objects_alive

