import tkinter as tk
from tkinter import ttk, messagebox

class FocusSession:
    """Stores information about the current study session."""

    def __init__(self, task_name, study_minutes, rest_minutes, total_loops):
        self.task_name = task_name
        self.study_minutes = study_minutes
        self.rest_minutes = rest_minutes
        self.total_loops = total_loops
        self.current_loop = 1
        self.time_left = 0  # seconds remaining; set by start()
        self.active = False  # True while a session is running

    def start(self):
        """Convert study minutes into seconds and store as the countdown value."""
        self.time_left = self.study_minutes * 60
        self.active = True

    def cancel(self):
        """Mark the session as no longer active."""
        self.active = False

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
        self.root.geometry("400x500")

        self.session = None  # will hold a FocusSession once Start Session is pressed

        self.create_widgets()

    def create_widgets(self):
        """Build and lay out all GUI widgets."""
        tk.Label(self.root, text="Task Name:").pack(pady=(10, 0))
        self.task_entry = tk.Entry(self.root, width=30)
        self.task_entry.pack(pady=5)

        tk.Label(self.root, text="Study Duration (minutes):").pack(pady=(10, 0))
        self.study_entry = tk.Entry(self.root, width=10)
        self.study_entry.pack(pady=5)

        tk.Label(self.root, text="Rest Duration (minutes):").pack(pady=(10, 0))
        self.rest_entry = tk.Entry(self.root, width=10)
        self.rest_entry.pack(pady=5)

        tk.Label(self.root, text="Number of Loops:").pack(pady=(10, 0))
        self.loops_entry = tk.Entry(self.root, width=10)
        self.loops_entry.pack(pady=5)

        self.timer_label = tk.Label(self.root, text="00:00", font=("Arial", 36))
        self.timer_label.pack(pady=20)

        self.start_button = tk.Button(self.root, text="Start Session", command=self.start_session)
        self.start_button.pack(pady=10)

        self.cancel_button = tk.Button(
        self.root, text="Cancel Session", command=self.cancel_session, state="disabled")
        self.cancel_button.pack(pady=5)

    def reset_gui(self):
        """Re-enable inputs and reset the display after a session ends."""
        self.task_entry.config(state="normal")
        self.study_entry.config(state="normal")
        self.rest_entry.config(state="normal")
        self.loops_entry.config(state="normal")
        self.start_button.config(state="normal")
        self.cancel_button.config(state="disabled")
        self.timer_label.config(text="00:00")

    def update_timer(self):
        """Update the countdown display once a second until the session ends."""
        if not self.session.active:
            return  # session was cancelled — stop the after() chain

        minutes = self.session.time_left // 60
        seconds = self.session.time_left % 60
        self.timer_label.config(text=str(minutes).zfill(2) + ":" + str(seconds).zfill(2))

        if self.session.is_complete():
            self.session_complete()
            return

        self.session.tick()
        self.root.after(1000, self.update_timer)

    def cancel_session(self):
        """Ask for confirmation, then stop the running session if confirmed."""
        confirmed = messagebox.askyesno(
            "Cancel Session", "Are you sure you want to cancel this session?"
        )
        if not confirmed:
            return

        self.session.cancel()
        self.reset_gui()

    def session_complete(self):
        """Notify the user the session finished, then reset the GUI."""
        self.session.active = False
        messagebox.showinfo("Focus Session Manager", "Session Complete!")
        self.reset_gui()

    def parse_positive_int(self, value):
        """Return the int value if it's a valid positive whole number, otherwise None."""
        try:
            number = int(value)
        except ValueError:
            return None
        if number <= 0:
            return None
        return number

    def start_session(self):
        """Validate input, create a FocusSession, and start the countdown."""
        task = self.task_entry.get().strip()
        study_minutes = self.parse_positive_int(self.study_entry.get().strip())
        rest_minutes = self.parse_positive_int(self.rest_entry.get().strip())
        total_loops = self.parse_positive_int(self.loops_entry.get().strip())

        if task == "":
            messagebox.showerror("Error", "Please enter a task name.")
            return

        if study_minutes is None:
            messagebox.showerror("Error", "Please enter a valid study duration.")
            return

        if rest_minutes is None:
            messagebox.showerror("Error", "Please enter a valid rest duration.")
            return

        if total_loops is None:
            messagebox.showerror("Error", "Please enter a valid number of loops.")
            return

        self.task_entry.config(state="disabled")
        self.study_entry.config(state="disabled")
        self.rest_entry.config(state="disabled")
        self.loops_entry.config(state="disabled")
        self.start_button.config(state="disabled")
        self.cancel_button.config(state="normal")

        self.session = FocusSession(task, study_minutes, rest_minutes, total_loops)
        self.session.start()
        self.update_timer()


if __name__ == "__main__":
    root = tk.Tk()
    app = FocusSessionApp(root)
    root.mainloop()