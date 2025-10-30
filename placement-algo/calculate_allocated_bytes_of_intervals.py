###################################### CALCULATE BYTES OF THE FINAL INTERVALS AND STORE THEM TO OUTPUT FILE ############################################

# Function to calculate the Allocated Bytes of intervals to be placed on Dram and Optane.
# The returned value, is an array where the even elements are the bytes to be allocated on Optane, and odd elements 
# are the bytes to be allocated on Dram. For example, if the returned array is [1 kB, 2 kB, 3 kB]
# this means that the algorithm must place the first 1 kB to optane, the next 2 kB after that to Dram, and the final 3 kB to Optane.

def calculate_allocated_bytes_of_intervals(final_spikes, allocated_bytes):

    if not final_spikes:
        return None     # if no spikes were found, return None

    # Transform spikes to intervals, from seconds to indices
    # We monitored every 0.25 seconds, so we multiply by 4 to get the correct indices
    # For example, if we want to calculate interval from second 11.75 to second 12.75, 
    # We will sum array elemts between indices [47,51] (5 * 0.25 seconds = 5 elements) 
    transformed_intervals = [[int(start * 4), int(end * 4)] for start, end in final_spikes]

    allocated_bytes_summary = []

    # 1. Append Allocated Bytes before the first interval which is placed on Dram
    allocated_bytes_summary.append(sum(allocated_bytes[0:transformed_intervals[0][0]]))


    for i, (start_idx, end_idx) in enumerate(transformed_intervals):
        # 2. Append Allocated Bytes inside the interval which is placed on Dram
        allocated_bytes_summary.append(sum(allocated_bytes[start_idx:end_idx+1]))

        # 3. Append Allocated Bytes in between current and next  interval which is placed on Dram
        if i < len(transformed_intervals) - 1:
            next_start_idx = transformed_intervals[i + 1][0]
            allocated_bytes_summary.append(sum(allocated_bytes[end_idx+1:next_start_idx]))



    return allocated_bytes_summary
