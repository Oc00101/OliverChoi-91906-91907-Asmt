import tkinter as tk
from tkinter import ttk, messagebox

try:
    import pygetwindow as gw
    APP_DETECTION_AVAILABLE = True
except ImportError:
    APP_DETECTION_AVAILABLE = False

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

class AppMonitor:
    """Checks the currently active window against a list of approved applications."""

    def __init__(self, allowed_apps, root):
        self.allowed_apps = allowed_apps
        self.current_app = ""
        self.warning_shown = False  # avoids repeating the warning every check
        self.root = root  # needed to bring the window to the front before warning

    def check_active_app(self):
        """Return the title of the currently active window, or '' if unavailable."""
        if not APP_DETECTION_AVAILABLE:
            return ""
        try:
            active_window = gw.getActiveWindow()
            if active_window is None:
                return ""
            return active_window.title
        except Exception:
            return ""

    def is_allowed(self, window_title):
        """Return True if the window title contains any approved app name."""
        if not self.allowed_apps:
            return True  # nothing selected means nothing to enforce
        for app_name in self.allowed_apps:
            if app_name.lower() in window_title.lower():
                return True
        return False

    def show_warning(self):
        """Bring the app to the front, then display a warning about the unapproved app."""
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after_idle(self.root.attributes, "-topmost", False)
        self.root.focus_force()

        messagebox.showwarning(
            "Unapproved Application Detected",
            "You are currently using an application that is not on your approved list.",
        )

class FocusSessionApp:
    """Creates the GUI, gets user input, and runs the countdown session."""

    def __init__(self, root):
        self.root = root
        self.root.title("Focus Session Manager")
        self.root.geometry("420x580")

        self.session = None  # will hold a FocusSession once Start Session is pressed
        self.app_monitor = None  # will hold an AppMonitor once Start Session is pressed

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

        tk.Label(self.root, text="Approved Applications", font=("Arial", 12, "bold")).pack(pady=(15, 0))

        self.app_choices = ["Google Chrome", "Microsoft Word", "Calculator", "Spotify"]
        self.app_vars = {}  # maps app name -> BooleanVar for its checkbox

        for app_name in self.app_choices:
            var = tk.BooleanVar(value=False)
            checkbox = tk.Checkbutton(self.root, text=app_name, variable=var)
            checkbox.pack(anchor="w", padx=40)
            self.app_vars[app_name] = var

        if not APP_DETECTION_AVAILABLE:
            tk.Label(self.root, text="(App detection is only supported on Windows, please pip install pygetwindow in cmd)", font=("Arial", 8, "italic"), fg="gray").pack(pady=(0, 5))                
            
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

    def check_apps(self):
        """Periodically check the active window against the approved list."""
        if not self.session.active:
            return  # session ended or was cancelled — stop the after() chain

        active_title = self.app_monitor.check_active_app()

        if active_title:  # only evaluate if we actually got a window title
            if self.app_monitor.is_allowed(active_title):
                self.app_monitor.warning_shown = False
            elif not self.app_monitor.warning_shown:
                self.app_monitor.warning_shown = True
                self.app_monitor.show_warning()

        self.root.after(2000, self.check_apps)

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

        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after_idle(self.root.attributes, "-topmost", False)
        self.root.focus_force()

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

        allowed_apps = [name for name, var in self.app_vars.items() if var.get()]

        self.session = FocusSession(task, study_minutes, rest_minutes, total_loops)
        self.session.start()

        self.app_monitor = AppMonitor(allowed_apps, self.root)
        self.update_timer()
        self.check_apps()


if __name__ == "__main__":
    root = tk.Tk()
    app = FocusSessionApp(root)
    root.mainloop()