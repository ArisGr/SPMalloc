import heapq
from intervaltree import IntervalTree

# Function to calculate the sum of allocated_bytes of a spike based on its start/end time
def calculate_allocated_bytes(ao_spike, allocated_objects):
    start_time, end_time = ao_spike
    start_idx = int(start_time * 4)  # Convert seconds to 0.25s elements, since we monitored allocated bytes every 0.25s
    end_idx = int(end_time * 4)  
    return sum(allocated_objects[start_idx:end_idx+1])


###################################### BUILD INTERVAL TREE FROM ACTIVE OBJECT SPIKES ############################################

def build_interval_tree(ao_spikes):
    interval_tree = IntervalTree()
    for index, (start_time, end_time) in enumerate(ao_spikes):
        interval_tree[start_time:end_time] = index  # Store both the index and the start/end times as a tuple

    return interval_tree


###################################### ACTIVE OBJECT SPIKE DETECTOR BASED ON K-MAX SELECTION ############################################

# Function to  select the active object spikes most prossibly linked to bandwidth spikes using the interval tree.
# For each pair of bw spikes, the function selects the top k ao spikes in between them based on their allocated bytes. 

def top_k_spike_selector(ao_spikes, allocated_objects, bw_spikes, k):
    interval_tree = build_interval_tree(ao_spikes)  # Build the interval tree from AO spikes
    selected_ao_spikes = []

    # Iterate over each bandwidth spike
    for i, bw_spike in enumerate(bw_spikes):
        bw_end_time = bw_spike[1]    # Get the end time of the current bw_spike
        previous_end_time = bw_spikes[i - 1][1] if i > 0 else None  # Get the end time of the previous bw_spike if there is one

        # Query the interval tree for AO spikes in between the two bw spikes
        if previous_end_time is not None:
            candidate_intervals = interval_tree[previous_end_time:bw_end_time]
        else:
            candidate_intervals = interval_tree[:bw_end_time]

        if not candidate_intervals:
            continue  # Skip if no candidates found

        heap = []  # This will store the top k AO spikes in the form of a min-heap


        for interval in candidate_intervals:
            ao_index = interval.data  # Extract the index of the AO spike
            ao_start_time = ao_spikes[ao_index][0]  # Get the start time of the AO spike

            # Only consider AO spikes that start within the valid range
            if previous_end_time is None or (previous_end_time < ao_start_time < bw_end_time):
                allocated = calculate_allocated_bytes(ao_spikes[ao_index], allocated_objects)  # Calculate allocated bytes of the ao spike
                heapq.heappush(heap, (allocated, ao_spikes[ao_index]))                         # and put it in the heap

                # If the heap grows larger than k, remove the smallest element
                if len(heap) > k:
                    heapq.heappop(heap)


        top_k_spikes = heapq.nlargest(k, heap)  # Get the top k spikes

        # Store the top k spikes (time intervals in seconds)
        for _, selected_ao_spike in top_k_spikes:
            selected_ao_spikes.append(selected_ao_spike)

    return selected_ao_spikes
