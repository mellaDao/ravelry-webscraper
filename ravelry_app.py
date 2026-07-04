import threading
import tkinter as tk
from tkinter import END, Frame, messagebox
import traceback

from ravelry_auth import create_session
from ravelry_core import run_pipeline
from storage import init_db
from screens.login_screen import LoginScreen
from screens.main_screen import MainScreen
from screens.results_screen import ResultsScreen

MODE_SCRAPE = 1
MODE_SENTIMENT = 2
MODE_BOTH = 3

class RavelryApp:
    # on startup, create initial window and first show the login screen
    def __init__(self):
        self.window = tk.Tk()
        self.window.geometry("520x580")
        self.window.title("Ravelry Project Scraper")

        init_db() # initialize db

        self.session = None
        self.username = None
        self.current_frame = None

        self.show_login_screen()

        self.cancel_event = threading.Event() # mostly to track whether the scraping event needs to be cancelled

    # wipes the current screen
    def clear_frame(self):
        if self.current_frame is not None:
            self.current_frame.destroy()
            self.current_frame = None

    # show the login screen
    def show_login_screen(self):
        self.session = None
        self.username = None
        self.clear_frame()
        self.window.title("Ravelry Login")
        self.current_frame = Frame(self.window)
        self.current_frame.pack(fill="both", expand=True)
        LoginScreen(
            parent=self.current_frame,
            on_login=self.handle_login,
            on_load_credentials=self.load_credentials_into_form,
        )

    # show the main screen
    def show_main_screen(self):
        self.clear_frame()
        self.window.title("Ravelry Project Scraper")
        self.current_frame = Frame(self.window)
        self.current_frame.pack(fill="both", expand=True)
        MainScreen(
            parent=self.current_frame,
            username=self.username,
            on_submit=self.handle_submit,
            on_logout=self.safe_logout,
        )

    # try login
    def handle_login(self, username_entry, password_entry, login_button, status_label):
        username = username_entry.get().strip()
        password = password_entry.get()

        if not username or not password:
            messagebox.showerror("Missing Input", "Username and password are required.")
            return

        login_button.config(state="disabled")
        status_label.config(text="Status: Logging in...")

        def worker():
            try:
                session = create_session(username, password)
                self.session = session
                self.username = username
                self.window.after(0, self.show_main_screen)
            except Exception as error:
                error_text = str(error)
                self.window.after(0, lambda: messagebox.showerror("Login Failed", error_text)) 
                self.window.after(0, lambda: status_label.config(text=f"Status: Login failed. {error_text}"))
                self.window.after(0,lambda: login_button.config(state="normal"))

        threading.Thread(target=worker, daemon=True).start()

    def safe_logout(self):
        if messagebox.askyesno("Log Out", "Are you sure? Any running tasks will be cancelled."):
            self.cancel_event.set()
            self.show_login_screen()

    # handle submit
    def handle_submit(self, widgets):
        self.cancel_event.clear()
        pattern_slug = widgets["pattern_entry"].get().strip()
        train_csv_path = widgets["train_csv_entry"].get().strip()
        mode = widgets["mode_var"].get()
        status_label = widgets["status_label"]
        submit_button = widgets["submit_button"]

        if not pattern_slug and mode in {MODE_SCRAPE, MODE_BOTH}:
            messagebox.showerror("Missing Input", "Pattern slug is required for scraping.")
            return

        if mode in {MODE_SENTIMENT, MODE_BOTH} and not train_csv_path:
            messagebox.showerror("Missing Input", "Train CSV path is required for sentiment analysis.")
            return

        submit_button.config(state="disabled")
        status_label.config(text="Status: Starting...")

        def progress(message):
            try:
                self.window.after(0, lambda: status_label.config(text=f"Status: {message}"))
            except tk.TclError:
                pass

        def worker():
            try:
                result = run_pipeline(
                    mode=mode,
                    pattern_slug=pattern_slug,
                    session=self.session,
                    train_csv_path=train_csv_path,
                    cancel_event=self.cancel_event,
                    on_progress=progress,
                )

                if result["report"]:
                    progress("Done. Sentiment model report printed to console.")
                    print(result["report"])
                else:
                    progress("Done.")
            except Exception as error:
                traceback.print_exc()
                error_msg = str(error)
                self.window.after(0, lambda: messagebox.showerror("Error", error_msg))
                self.window.after(0, lambda: status_label.config(text=f"Status: Error: {error_msg}"))
            finally:
                self.window.after(0, lambda: submit_button.config(state="normal"))

        threading.Thread(target=worker, daemon=True).start()

    def run(self):
        self.window.mainloop()


def main():
    RavelryApp().run()

if __name__ == "__main__":
    main()
