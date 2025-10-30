from pathlib import Path

# Function to save allocated bytes to be placed on dram/optane to the output file. Each line denotes the allocated bytes to 
# be placed on Dram/Optane. 
# 1st line is the number of changes in the allocation type (dram/optane). Then starting from second line we have byte numbers.
# Bytes of 2nd line are placed on Dram, 3rd on Optane, 4th on Dram, 5th on Optane and so on ...
# This file is the input to SPMalloc for the dynamic placement

def save_to_file(allocated_bytes_summary):
    file_path = Path("output.txt")

    try:
        with file_path.open('w') as f:
            if allocated_bytes_summary is None:
                f.write("0\n")
                print("No spikes found — wrote 0 to output.txt")
                return
            
            f.write(f"{len(allocated_bytes_summary)}\n")
            for value in allocated_bytes_summary:
                f.write(f"{value}\n")

        print(f"Successfully wrote {len(allocated_bytes_summary)} entries to '{file_path.name}'")    

    except Exception as e:
        print(f"Error while writing to file: {e}")

    