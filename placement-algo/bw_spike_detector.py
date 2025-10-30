# ##################################################### BW SPIKE DETECTOR ########################################################
# Function to identify BW spikes by comparing the Dram write BW at each time stamp with the average Optane write BW
# of the sliding window of size s around that time stamp. High differences in those values, based on the
# percentile threshold pp which we define inside the code, signify bw spike regions.

def bw_spike_detector(dram_writes, optane_writes, window_size, sampling_interval=1, min_duration=4):
    # Intel pcm monitors every 1 second, so sampling_interval = 1.
    spikes = []
    in_spike = False
    spike_start = None
    pp = 3
    half_window = window_size // 2  # Half window size for averaging around the current index


    if not dram_writes or not optane_writes:
        return spikes

    avg_dram_writes = sum(dram_writes) / len(dram_writes)   # average dram write bw
    optane_avg = sum(optane_writes) / len(optane_writes)    # average optane write bw

    if avg_dram_writes  <= 1.3 * optane_avg :
        return spikes   # If average  Dram BW comparable to average Optane BW , we dont need to look for spikes
                        

    max_valid_index = min(len(dram_writes), len(optane_writes))
    for i in range(max_valid_index):
        current_bw = dram_writes[i]  # DRAM_BW[t]

        if window_size % 2 == 0:  # even window size
            start_window = max(0, i - half_window)                      # ti
            end_window = min(len(optane_writes), i + half_window)       # tj
        else:                     # odd window size
            start_window = max(0, i - half_window)                      # ti
            end_window = min(len(optane_writes), i + half_window + 1)   # tj

        optane_window = optane_writes[start_window:end_window] 

        avg_optane_bw = sum(optane_window) / len(optane_window) # Calculate the average of the optane writes in the window


        if current_bw > pp * avg_optane_bw and not in_spike:
            spike_start = i * sampling_interval  # Start spike if DRAM_BW[t] >  pp * avg(Optane_BW[s])
            in_spike = True                      


        elif current_bw < pp * avg_optane_bw and in_spike:
            spike_end = i * sampling_interval    # Stop spike if DRAM_BW[t] <  pp * avg(Optane_BW[s])
            middle_time = (spike_start + spike_end) / 2  


            if (spike_end - spike_start) >= min_duration:
                spikes.append((spike_start, spike_end, middle_time)) # Only consider the spike if it lasts longer than min_duration seconds (user defined)
            in_spike = False

    if in_spike:
        spike_end = max_valid_index * sampling_interval  # If still in a spike at the end of the loop, close it
        middle_time = (spike_start + spike_end) / 2

        if (spike_end - spike_start) >= min_duration:
            spikes.append((spike_start, spike_end, middle_time))

    return spikes
