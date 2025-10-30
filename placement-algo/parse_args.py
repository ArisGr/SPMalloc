import argparse
from pathlib import Path

# Function to parse arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Provide benchmark name, number of top AO spikes to select between bw spikes and window size for bw spike detector")

    parser.add_argument('-i', '--input_benchmark', type=str, required=True, help="Benchmark name (e.g., lulesh or streamcluster)")
    parser.add_argument('-k', '--top_k_ao_spikes', type=int, default=1, help="Number of top AO spikes to select (default: k = 1)")
    parser.add_argument('-s', '--window_size', type=int, default=5,help="Window size for detecting BW spikes (default: s = 5)")

    args = parser.parse_args()

    k = args.top_k_ao_spikes
    s = args.window_size
    benchmark_name = args.input_benchmark
    return k, s, benchmark_name

# Function to get file paths
def get_file_paths(benchmark_name):
    log_path = Path(f"{benchmark_name}_logfile.txt")
    optane_path = Path(f"{benchmark_name}_optane-pcm-memory.csv")
    dram_path = Path(f"{benchmark_name}_dram-pcm-memory.csv")

    return log_path, optane_path, dram_path
