import numpy as np

########################### ACTIVE OBJECTS SPIKE DETECTOR #######################################
# This function uses the active object number during the execution of the program to define regions where
# multiple objects are created, by examining the variation in their consecutive differences.
# Sharp changes in those values signify regions to be defined as active object spikes.

def ao_spike_detector(active_objects):
    tf = 2  #threshold factor
    consecutive_diffs = np.abs(np.diff(active_objects))   # Calculate absolute differences between consecutive elements   |a(i+1)-a(i)|
    overall_avg_consecutive_change = np.mean(consecutive_diffs) # Calculate the overall average change of consecutive elements 
    cd = tf * overall_avg_consecutive_change            # threshold cd
    spi = np.where(consecutive_diffs > cd)[0]           # spi formula

    filtered_spi = list(spi)
    filtered_spi.sort()    # sort the spikes

    # Now check for the neighboring spikes, and combine them into one big spike
    extended_spi = []
    for i in range(len(filtered_spi)):
        extended_spi.append(filtered_spi[i])

        if i < len(filtered_spi) - 1:
            current_index = filtered_spi[i]
            next_index = filtered_spi[i + 1]

            # If the gap between two spikes is 4 or less, merge the spikes by connecting all indexes in between
            if next_index - current_index <= 5:  # next - current <= 5 means gap of at most 4, user can change this value if he desires
                for missing in range(current_index + 1, next_index):
                    extended_spi.append(missing)


    extended_spi = sorted(set(extended_spi)) # Sort the extended spikes again


    if not extended_spi:
        return []   # If no spikes were found return

    # Now merge the continuing spikes into big ones
    spikes = []
    current_spike = [extended_spi[0]]  

    for i in range(1, len(extended_spi)):
        if extended_spi[i] == extended_spi[i - 1] + 1:  # Check if current spike is continuous
            current_spike.append(extended_spi[i])
        else:
            # If there's a gap, save the current spike and start a new one
            spikes.append(current_spike)
            current_spike = [extended_spi[i]]

    # Append the last collected spike
    spikes.append(current_spike)

    # Up until now, we worked with the indices of the arrays. Now we convert the indices to time for each spike and store it in time_spikes.
    # Keep in mind that we monitored the active objects each 0.25 seconds, so to get the time we multiply with 0.25.
    # For example the 5th element of the active objects array, corresponds to 4 * 0.25 = 1 second. This means that if the start index of a spike
    # is 4, then the spike start at second 1.
    # If the user monitored in some other frequency, lets say 0.1 sec, he will need to change 0.25 to the respective value, i.e. 0.1.

    time_spikes = []
    for spike in spikes:
        start_index = spike[0]
        num_elements = len(spike)  
        start_time = start_index * 0.25 
        end_time = start_time + (num_elements * 0.25) 

        time_spikes.append([start_time, end_time])

    # Filter  purely negative spikes spikes, if no increment is found then we have no valid_spikes
    valid_spikes = []
    for spike in time_spikes:
        start_time = spike[0]
        end_time = spike[1]

        start_index = int(start_time * 4)  # Multiply by 4 since each element represents 0.25s
        end_index = int(end_time * 4)      

        # Check for increments in consecutive active_objects inside the spike
        increment_found = False
        for i in range(start_index, end_index):
            if active_objects[i] < active_objects[i + 1]:
                increment_found = True
                break

        # If an increment is found, keep this spike
        if increment_found:
            valid_spikes.append(spike)

    return valid_spikes
