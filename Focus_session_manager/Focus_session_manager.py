import tkinter as tk
from tkinter import ttk, messagebox

# --- Set up the main window ---
root = tk.Tk()
root.title("Focus Session Manager")
root.geometry("400x400")
time_left = 0  # this will store how many seconds are left in the session

# --- Widgets---
# Task name input
tk.Label(root, text="Task Name:").pack(pady=(10, 0))
task_entry = tk.Entry(root, width=30)
task_entry.pack(pady=5)

# Duration selector (dropdown)
tk.Label(root, text="Study Duration (minutes):").pack(pady=(10, 0))
duration_var = tk.StringVar() #stores the value of the selected duration
duration_menu = ttk.Combobox(root, textvariable=duration_var, values=["15", "20", "25", "30"], state="readonly") #read only
duration_menu.pack(pady=5)

# Timer display label
timer_label = tk.Label(root, text="00:00", font=("Arial", 36))
timer_label.pack(pady=20)

# Start button
start_button = tk.Button(root, text="Start Session")
start_button.pack(pady=10)


# Functions
def reset_gui():
    task_entry.config(state="normal")
    duration_menu.config(state="readonly")
    start_button.config(state="normal")
    timer_label.config(text="00:00")

def update_timer():
    """
    This function runs once every second while the timer is counting down.
    It updates the label on screen, then schedules itself to run again.
    """
    global time_left

    # Convert time_left (in seconds) into minutes and seconds for display
    minutes = time_left // 60  # // means "divide and round down"
    seconds = time_left % 60   # % gives the remainder (leftover seconds)

    # zfill(2)(zero fill) makes sure numbers show as "05" instead of "5"
    timer_label.config(text=str(minutes).zfill(2) + ":" + str(seconds).zfill(2))

    # Check if the countdown has finished
    if time_left == 0:
        messagebox.showinfo("Focus Session Manager", "Session Complete!")
        reset_gui()  # reset the GUI so the user can start a new session
        return  # stops 

    time_left = time_left - 1  # one second has now passed, so reduce the count

    # built-in method used to schedule the execution of a function after a specific time delay
    # it means "Wait 1000 milliseconds (1 second), then call update_timer() again."
    root.after(1000, update_timer)

def start_session():
    #This function runs once, when the Start Session button is clicked. It checks the user's input, then starts the countdown.
    
    global time_left # this allows me to use a variable that is outside of this function.

    task = task_entry.get().strip() # get the text typed in the task box
    duration = duration_var.get() # get the selected duration

    # --- Input validation ---
    if task == "":
        messagebox.showerror("Error", "Please enter a task name you would like to work on.")
        return  # stop here, don't start the timer

    if duration == "":
        messagebox.showerror("Error", "Please select a duration.")
        return

    # Lock the inputs so they can't be changed while the session is running
    task_entry.config(state="disabled")
    duration_menu.config(state="disabled")
    start_button.config(state="disabled")

    # Convert minutes into seconds, since my timer counts down in seconds
    time_left = int(duration) * 60

    """Start the countdown by calling update_timer() for the first time.
    From here, update_timer() will keep calling itself every second
    using root.after(), until time_left reaches 0."""
    update_timer()


# Connect the button to the start_session function
start_button.config(command=start_session)
root.mainloop()