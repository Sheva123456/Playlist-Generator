import customtkinter as ctk
import main2 
import json 

# Set default theme for the GUI
ctk.set_default_color_theme("green")

# Load genres and artists from song data
genres, artists = main2.get_artists_genres()

# Load full song data from JSON
with open("songs5.json", "r") as f:
    songs_data = json.load(f)

# Fast lookup dictionary: song name -> song data
song_map = {song["name"]: song for song in songs_data}

# Display a temporary message on the given frame for 1.5 seconds
def show_temp_message(root, text): 
    msg = ctk.CTkLabel(
        root,
        text=text,
        fg_color="#AEC3C7",
        text_color="black",
        corner_radius=8,
        pady=5,
        padx=10
    ) 
    msg.place(relx=0.5, rely=0.1, anchor="center")  # Position at top center
    root.after(1500, msg.destroy)  # Auto-destroy after 1.5s

# App state to store selected genres and artists
app_state = {
    "selected_genres": [],
    "selected_artists": []
}

# ----- NAVIGATION BETWEEN FRAMES -----

def show_genre_survey():
    """Hide home frame and show genre survey frame"""
    home_frame.pack_forget()
    genre_frame.pack(fill="both", expand=True)

def show_artist_survey():
    """Hide genre frame and show artist survey frame"""
    genre_frame.pack_forget()
    artist_frame.pack(fill="both", expand=True)

# ----- SURVEY HANDLING -----

def finish_genres():
    """Handle finishing genre selection"""
    selected = []
    for g, var in genre_vars:
        if var.get():
            selected.append(g)
    
    if not selected:  # Validate at least one box ticked
        show_temp_message(genre_frame, "please tick at least one box")
        return
    else: 
        app_state["selected_genres"] = selected
        genre_frame.pack_forget()
        show_artist_survey()

def finish_artists():
    """Handle finishing artist selection and apply preferences"""
    selected = []
    for a, var in artist_vars:
        if var.get():
            selected.append(a)
    
    if not selected:  # Validate at least one box ticked
        show_temp_message(artist_frame, "please tick at least one box")
        return
    else: 
        app_state["selected_artists"] = selected
        artist_frame.pack_forget()
        # Apply user preferences to songs
        main2.apply_survey_preferences(app_state["selected_genres"], app_state["selected_artists"])
        update_generate_button()
        intro_label.place_forget()
        home_frame.pack(fill="both", expand=True)

# Enable or hide the playlist generation button and dropdown based on selections
def update_generate_button():
    if app_state["selected_artists"] and app_state["selected_genres"]:
        generate_button.pack(side="left", padx=10)
        mode_dropdown.pack(side="left", padx=10)
        button_row.pack(pady=20)
    else:
        generate_button.pack_forget()
        mode_dropdown.pack_forget()
        button_row.pack_forget()

# Update the switch text depending on its state
def update_switch_text():
    if switch_var.get():
        my_switch.configure(text="Memoization")
    else:
        my_switch.configure(text="Tabulation")

# ----- PLAYLIST GENERATION -----

def generate_playlist():
    """Generate a playlist based on selected options and display in the GUI"""
    mode = playlist_mode.get()  # Read selected mode from dropdown
    
    # Validate time limit is set
    if main2.time_limit == 0:
        show_temp_message(home_frame, "Please set a time limit first")
        return
    
    # Determine whether to use memoization or tabulation
    memo = switch_var.get()

    # Call main2.run_knapsack depending on selected mode
    if mode == "Pure Knapsack":
        (value, chosen), runtime = main2.time_it(main2.run_knapsack, memo)
    elif mode == "For You":
        (value, chosen), runtime = main2.time_it(main2.run_knapsack, memo, False, True)
    elif mode == "Surprise Me":
        (value, chosen), runtime = main2.time_it(main2.run_knapsack, memo, True, False)

    # Clear previous playlist display
    for widget in p_scroll_frame.winfo_children():
        widget.destroy()
    
    total_duration = 0 
        
    # Display each chosen song as a card in the scroll frame
    for song_name in chosen:
        song = song_map[song_name]
        artist = song["artist"]
        duration = song["duration"]
        minutes = duration // 60
        seconds = duration % 60
        time_str = f"{minutes}:{seconds:02d}"
        total_duration += duration
        total_minutes = total_duration // 60
        total_seconds = total_duration % 60  
        total_time_str = f"{total_minutes}:{total_seconds:02d}"

        # Song card frame
        card = ctk.CTkFrame(p_scroll_frame, corner_radius=10, height=100, fg_color="#222222")
        card.pack(fill="x", pady=5, padx=10)
        
        # Song name and artist label
        text = f"{song_name} • {artist}"
        lbl = ctk.CTkLabel(card, text=text, anchor="w")
        lbl.pack(padx=10, pady=10, side="left")
        
        # Duration label
        duration_lbl = ctk.CTkLabel(card, text=time_str)
        duration_lbl.pack(padx=10, pady=10, side="right")
    
        # Update total statistics labels
        total_time_label.configure(text="Total Length: " + total_time_str)
        total_enjoyment_label.configure(text="Total Enjoyment: " + f"{value}")
        total_runtime_label.configure(text="Thought for " + f"{runtime:.3f}" + " Seconds")

# ----- TIME LIMIT HANDLING -----

def on_set_time():
    """Handle setting the time limit from user input"""
    user_input = entry.get()

    # Validate numeric input
    if not user_input.isdigit():
        show_temp_message(home_frame, "Please enter numbers only")
        return

    show_temp_message(home_frame, "Time limit set successfully")
    minutes = int(user_input)
    main2.set_time_limit(minutes)

# ----- GUI SETUP -----

root = ctk.CTk()
root.geometry("800x500")
root.title("Playlist Generator")

# ----- HOME PAGE -----
home_frame = ctk.CTkFrame(root)
home_frame.pack(fill="both", expand=True)
home_frame.grid_rowconfigure(0, weight=1)
home_frame.grid_columnconfigure(0, weight=1)

# Playlist display frame inside home frame
playlist_frame = ctk.CTkFrame(home_frame, fg_color="gray20")
p_scroll_frame = ctk.CTkScrollableFrame(playlist_frame, fg_color="gray20")
p_scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
playlist_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Button to take the survey
survey_btn = ctk.CTkButton(home_frame, text="Take Survey", command=show_genre_survey) 
survey_btn.pack(pady=10)

# Intro label displayed before generating playlist
intro_label = ctk.CTkLabel(playlist_frame, text="Welcome! In order to create a playlist, please fill in the music survey")
intro_label.place(relx=0.5, rely=0.5, anchor="center")

# ----- GENRE SURVEY -----
genre_frame = ctk.CTkFrame(root)
g_scroll_frame = ctk.CTkScrollableFrame(genre_frame, label_text="Choose Your Favorite Genres")
g_scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

genre_vars = []
for g in genres:
    var = ctk.BooleanVar()
    chk = ctk.CTkCheckBox(g_scroll_frame, text=g, variable=var)
    chk.pack(anchor="w")
    genre_vars.append((g, var))

genre_done_btn = ctk.CTkButton(genre_frame, text="Finish", command=finish_genres)
genre_done_btn.pack(pady=20)

# ----- ARTIST SURVEY -----
artist_frame = ctk.CTkFrame(root)
a_scroll_frame = ctk.CTkScrollableFrame(artist_frame, label_text="Choose Your Favorite Artists")
a_scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

artist_vars = []
for a in artists:
    var = ctk.BooleanVar()
    chk = ctk.CTkCheckBox(a_scroll_frame, text=a, variable=var)
    chk.pack(anchor="w")
    artist_vars.append((a, var))

artist_done_btn = ctk.CTkButton(artist_frame, text="Finish", command=finish_artists)
artist_done_btn.pack(pady=20)

# ----- PLAYLIST GENERATION BUTTONS -----
playlist_mode = ctk.StringVar(value="Pure Knapsack") 
button_row = ctk.CTkFrame(home_frame)
button_row.pack_forget()

generate_button = ctk.CTkButton(button_row, text="Generate Playlist", command=generate_playlist)
generate_button.pack_forget()

mode_dropdown = ctk.CTkOptionMenu(button_row, variable=playlist_mode, values=["Pure Knapsack", "For You", "Surprise Me"])
mode_dropdown.pack_forget()

# Labels to display total time, enjoyment, and runtime
totals_frame = ctk.CTkFrame(home_frame, fg_color="transparent")
totals_frame.pack(pady=5)

total_time_label = ctk.CTkLabel(totals_frame, text="", text_color="white")
total_time_label.pack(side="left", padx=10)

total_enjoyment_label = ctk.CTkLabel(totals_frame, text="", text_color="white")
total_enjoyment_label.pack(side="left", padx=10)

total_runtime_label = ctk.CTkLabel(totals_frame, text="", text_color="white")
total_runtime_label.pack(side="left", padx=10)

# ----- TABULATION / MEMO SWITCH -----
switch_var = ctk.BooleanVar(value=False)
my_switch = ctk.CTkSwitch(button_row, text="Tabulation", variable=switch_var, command=update_switch_text, width=140)
my_switch.pack(padx=10, pady=10, side="right")

# ----- TIME LIMIT INPUT -----
entry = ctk.CTkEntry(button_row, placeholder_text="Set time limit (Minutes)")
entry.pack(side="left", padx=10)

button = ctk.CTkButton(button_row, text="Set Time Limit", command=on_set_time)
button.pack(side="left", padx=10, pady=10)

# Start the GUI main loop
root.mainloop()
