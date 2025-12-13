import json
import time
import numpy


# File storing song data
SONG_FILE = "songs5.json"
time_limit = 0  # Global time limit in seconds for the knapsack algorithm

# Utility function to measure execution time of a function
def time_it(func, *args, **kwargs):
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()
    return result, end - start

# Set the global time limit in minutes
def set_time_limit(minutes):
    global time_limit
    time_limit = 60 * minutes  # Convert minutes to seconds

# Load songs data from JSON file
def load_songs():
    with open(SONG_FILE, "r") as f:
        return json.load(f)

# Save songs data back to JSON file
def save_songs(data):
    with open(SONG_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Extract key fields from songs data for easier processing
def extract_fields(data):
    durations = [s["duration"] for s in data]
    enjoyment = [s["enjoyment"] for s in data]
    adjusted = [s["adjusted_enjoyment"] for s in data]
    names = [s["name"] for s in data]
    
    return durations, enjoyment, adjusted, names

# Knapsack dynamic programming using tabulation (iterative)
def knapsack_tabulation(capacity, weight, value, names):
    n = len(weight)
    K = [[0]*(capacity+1) for _ in range(n+1)]  # DP table initialization

    # Build table in bottom-up manner
    for i in range(1, n+1):
        for c in range(capacity+1):
            if weight[i-1] <= c:
                K[i][c] = max(
                    value[i-1] + K[i-1][c - weight[i-1]],  # Include current item
                    K[i-1][c]  # Exclude current item
                )
            else:
                K[i][c] = K[i-1][c]  # Cannot include current item

    # Backtracking to find chosen items
    chosen = []
    i, c = n, capacity
    while i > 0 and c > 0:
        if K[i][c] != K[i-1][c]:
            chosen.append(names[i-1])
            c -= weight[i-1]
        i -= 1

    return K[n][capacity], chosen[::-1]  # Return max value and list of chosen songs

# Knapsack dynamic programming using memoization (recursive)
def knapsack_memo(capacity, weight, value, names, n, memo=None):
    if memo is None:
        memo = {}  # Dictionary to store computed subproblems

    if (n, capacity) in memo:
        return memo[(n, capacity)]

    if n == 0 or capacity == 0:  # Base case
        return 0, []

    if weight[n-1] > capacity:  # Cannot include current item
        ans = knapsack_memo(capacity, weight, value, names, n-1, memo)
        memo[(n, capacity)] = ans
        return ans

    # Include current item
    inc_val, inc_items = knapsack_memo(capacity - weight[n-1], weight, value, names, n-1, memo)
    inc_val += value[n-1]
    inc_items = inc_items + [names[n-1]]

    # Exclude current item
    exc_val, exc_items = knapsack_memo(capacity, weight, value, names, n-1, memo)

    # Choose the better option
    best = (inc_val, inc_items) if inc_val > exc_val else (exc_val, exc_items)
    memo[(n, capacity)] = best
    return best

# Mark chosen songs as listened
def save_listened(chosen, data):
    for song in data:
        if song["name"] in chosen:
            song["listened_before"] = 1

# Update recently listened count and adjust enjoyment
def update_recently_listened(chosen, data):
    for song in data:
        if song["name"] in chosen:
            song["recently_listened"] += 1
            song["adjusted_enjoyment"] = max(0, song["adjusted_enjoyment"] - 0.5)

        # Reset adjusted enjoyment if recently listened hits threshold
        if song["recently_listened"] >= 5:
            song["adjusted_enjoyment"] = min(10, song["adjusted_enjoyment"] + 2.5)
            song["recently_listened"] = 0
    save_songs(data)

# Get list of songs that haven't been played yet
def get_unplayed_songs(data):
    return [s for s in data if s["listened_before"] == 0]

# Get unique genres and artists from song data
def get_artists_genres():
    data = load_songs()
    genres = sorted({song["genre"] for song in data})
    artists = sorted({song["artist"] for song in data})
    return genres, artists

# Reset all songs to unplayed and enjoyment back to original
def reset_songs():
    data = load_songs()
    for s in data:
        s["listened_before"] = 0
        s["recently_listened"] = 0
        s["adjusted_enjoyment"] = s["enjoyment"]
    save_songs(data)

# Reset enjoyment for all songs to default value 5
def reset_enjoyment_all():
    data = load_songs()
    for s in data:
        s["enjoyment"] = 5
        s["adjusted_enjoyment"] = 5
    save_songs(data)

# Apply user survey preferences to boost enjoyment
def apply_survey_preferences(fav_genres, fav_artists):
    reset_enjoyment_all()
    reset_songs()
    
    data = load_songs()
    for s in data:
        boost = 0
        if s["genre"] in fav_genres: boost += 2
        else: 
            boost -= 1 
        
        if s["artist"] in fav_artists: boost += 3
        
        # Boost based on global playcount (logarithmic)
        boost += 1/7 * numpy.log(s["global_playcount"])
        
        rounded_enjoyment = min(10,max(0,s["enjoyment"] + boost))
        
        # Scale to integer for knapsack (1 decimal precision)
        s["enjoyment"] = int(round(rounded_enjoyment * 10))  
        s["adjusted_enjoyment"] = s["enjoyment"]
    save_songs(data)

# General function to run knapsack algorithm
def run_knapsack(use_memo=False, only_unplayed=False, use_adjusted=False):
    data = load_songs()
    songs = get_unplayed_songs(data) if only_unplayed else data

    durations = [s["duration"] for s in songs]
    values = [s["adjusted_enjoyment"] if use_adjusted else s["enjoyment"] for s in songs]
    names = [s["name"] for s in songs]

    if use_memo:
        value, chosen = knapsack_memo(time_limit, durations, values, names, len(songs))
    else:
        value, chosen = knapsack_tabulation(time_limit, durations, values, names)

    save_listened(chosen, data)
    update_recently_listened(chosen, data)
    return value, chosen

# Predefined playlist strategies
def surprise_me_tabulation():
    return run_knapsack(use_memo=False, only_unplayed=True, use_adjusted=False)

def surprise_me_memoization():
    return run_knapsack(use_memo=True, only_unplayed=True, use_adjusted=False)

def for_you_tabulation():
    return run_knapsack(use_memo=False, only_unplayed=False, use_adjusted=True)

def for_you_memoization():
    return run_knapsack(use_memo=True, only_unplayed=False, use_adjusted=True)
