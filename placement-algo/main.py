from parse_args import parse_args, get_file_paths
from extract_info import extract_csv, extract_txt
from ao_spike_detector import ao_spike_detector
from bw_spike_detector import bw_spike_detector
from top_k_spike_selector import top_k_spike_selector
from calculate_allocated_bytes_of_intervals import calculate_allocated_bytes_of_intervals
from save_to_file import save_to_file

name = ""

def main():
    
    k, s, benchmark_name = parse_args() # Parse arguments

    log_path, optane_file, dram_file = get_file_paths(benchmark_name) # Get file paths 

    optane_writes, dram_writes = extract_csv(optane_file, dram_file) # Extract optane and dram write bandwidths

    allocated_bytes, objects_alive = extract_txt(log_path) # Parse the log file to get allocated_bytes and objects_alive arrays

    ao_spikes = ao_spike_detector(objects_alive) # Detect active-object spikes and bandwidth spikes
    bw_spikes = bw_spike_detector(dram_writes, optane_writes, s)

    final_spikes = top_k_spike_selector(ao_spikes, allocated_bytes, bw_spikes, k) # Select top-k AO spikes (uses interval tree internally)
    final_spikes = sorted(final_spikes, key=lambda x: x[0])  # Sort those spikes based on their start time

    allocated_bytes_summary = calculate_allocated_bytes_of_intervals(final_spikes, allocated_bytes) # Calculate the allocated bytes inside those spikes

    save_to_file(allocated_bytes_summary) # Save results to output file

if __name__ == "__main__":
    main()
