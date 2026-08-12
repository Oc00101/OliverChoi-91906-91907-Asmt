import tkinter as tk
from tkinter import ttk, messagebox


class FocusSession:
    """Stores information about the current study session."""

    def __init__(self, task_name, study_minutes):
        self.task_name = task_name
        self.study_minutes = study_minutes
        self.time_left = 0  # seconds remaining; set by start()

    def start(self):
        """Convert study minutes into seconds and store as the countdown value."""
        self.time_left = self.study_minutes * 60

    def tick(self):
        """Reduce the remaining time by one second."""
        self.time_left -= 1

    def is_complete(self):
        """Return True once the countdown has reached zero."""
        return self.time_left <= 0


class FocusSessionApp:
    """Creates the GUI, gets user input, and runs the countdown session."""

    def __init__(self, root):
        self.root = root
        self.root.title("Focus Session Manager")
        self.root.geometry("400x400")

        self.session = None  # will hold a FocusSession once Start Session is pressed

        self.create_widgets()

    def create_widgets(self):
        """Build and lay out all GUI widgets."""
        tk.Label(self.root, text="Task Name:").pack(pady=(10, 0))
        self.task_entry = tk.Entry(self.root, width=30)
        self.task_entry.pack(pady=5)

        tk.Label(self.root, text="Study Duration (minutes):").pack(pady=(10, 0))
        self.duration_var = tk.StringVar()
        self.duration_menu = ttk.Combobox(
            self.root,
            textvariable=self.duration_var,
            values=["15", "20", "25", "30"],
            state="readonly",
        )
        self.duration_menu.pack(pady=5)

        self.timer_label = tk.Label(self.root, text="00:00", font=("Arial", 36))
        self.timer_label.pack(pady=20)

        self.start_button = tk.Button(self.root, text="Start Session", command=self.start_session)
        self.start_button.pack(pady=10)

    def reset_gui(self):
        """Re-enable inputs and reset the display after a session ends."""
        self.task_entry.config(state="normal")
        self.duration_menu.config(state="readonly")
        self.start_button.config(state="normal")
        self.timer_label.config(text="00:00")

    def update_timer(self):
        """Update the countdown display once a second until the session ends."""
        minutes = self.session.time_left // 60
        seconds = self.session.time_left % 60
        self.timer_label.config(text=str(minutes).zfill(2) + ":" + str(seconds).zfill(2))

        if self.session.is_complete():
            self.session_complete()
            return

        self.session.tick()
        self.root.after(1000, self.update_timer)

    def session_complete(self):
        """Notify the user the session finished, then reset the GUI."""
        messagebox.showinfo("Focus Session Manager", "Session Complete!")
        self.reset_gui()

    def start_session(self):
        """Validate input, create a FocusSession, and start the countdown."""
        task = self.task_entry.get().strip()
        duration = self.duration_var.get()

        if task == "":
            messagebox.showerror("Error", "Please enter a task name you would like to work on.")
            return

        if duration == "":
            messagebox.showerror("Error", "Please select a duration.")
            return

        self.task_entry.config(state="disabled")
        self.duration_menu.config(state="disabled")
        self.start_button.config(state="disabled")

        self.session = FocusSession(task, int(duration))
        self.session.start()
        self.update_timer()


if __name__ == "__main__":
    root = tk.Tk()
    app = FocusSessionApp(root)
    root.mainloop()