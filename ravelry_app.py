import threading
import tkinter as tk
from tkinter import END, Button, Entry, Frame, IntVar, Label, Radiobutton, messagebox

from ravelry_auth import create_session, load_credentials_from_file
from ravelry_core import run_pipeline

FONT_NAME = "Segoe UI"
FONT_TITLE_SIZE = 20
FONT_BODY_SIZE = 12
FONT_STYLE = ""

MODE_SCRAPE = 1
MODE_SENTIMENT = 2
MODE_BOTH = 3

class RavelryApp:
    # on startup, create initial window and first show the login screen
    def __init__(self):
        self.window = tk.Tk()
        self.window.geometry("520x660")
        self.window.title("Ravelry Project Scraper")

        self.session = None
        self.username = None
        self.current_frame = None

        self.show_login_screen()

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
        self.build_login_screen(self.current_frame)

    # show the main screen
    def show_main_screen(self):
        self.clear_frame()
        self.window.title("Ravelry Project Scraper")
        self.current_frame = Frame(self.window)
        self.current_frame.pack(fill="both", expand=True)
        self.build_main_screen(self.current_frame)

    # build login screen
    def build_login_screen(self, parent):
        # center everything in a frame
        center_frame = Frame(parent)
        center_frame.pack(expand=True)

        Label(
        center_frame,
        text="Ravelry Login",
        font=(FONT_NAME, FONT_TITLE_SIZE, FONT_STYLE),
        ).grid(row=0, column=0, columnspan=2, pady=(0, 30))

        # form fields
        Label(center_frame, text="Username", font=(FONT_NAME, FONT_BODY_SIZE, FONT_STYLE)).grid(row=1, column=0, sticky="e", padx=(0, 10), pady=8)
        username_entry = Entry(center_frame, width=30)
        username_entry.grid(row=1, column=1, pady=8)

        Label(center_frame, text="Password", font=(FONT_NAME, FONT_BODY_SIZE, FONT_STYLE)).grid(row=2, column=0, sticky="e", padx=(0, 10), pady=8)
        password_entry = Entry(center_frame, width=30, show="*")
        password_entry.grid(row=2, column=1, pady=8)

        Label(center_frame, text="Config Key", font=(FONT_NAME, FONT_BODY_SIZE, FONT_STYLE)).grid(row=3, column=0, sticky="e", padx=(0, 10), pady=8)
        key_entry = Entry(center_frame, width=30, show="*")
        key_entry.grid(row=3, column=1, pady=8)

        # buttons
        Button(
            center_frame,
            text="Load Saved Credentials",
            command=lambda: self.load_credentials_into_form(
                username_entry, password_entry, key_entry, status_label
            ),
        ).grid(row=4, column=0, columnspan=2, pady=(20, 8))

        login_button = Button(
            center_frame,
            text="Login",
            width=20,
            bg="brown",
            fg="white",
            command=lambda: self.handle_login(
                username_entry, password_entry, login_button, status_label
            ),
        )
        login_button.grid(row=5, column=0, columnspan=2, pady=8)

        # status
        status_label = Label(
            center_frame,
            text="Status: Enter credentials to log in.",
            font=(FONT_NAME, FONT_BODY_SIZE, FONT_STYLE),
            wraplength=380,
            justify="left",
        )
        status_label.grid(row=6, column=0, columnspan=2, pady=(20, 8))

        Label(
            center_frame,
            text="Uses login-config.xml if present, otherwise login-info.txt.",
            font=(FONT_NAME, 10, FONT_STYLE),
        ).grid(row=7, column=0, columnspan=2)

        Label(
            center_frame,
            text="Config key is required for encrypted login-config.xml.",
            font=(FONT_NAME, 10, FONT_STYLE),
        ).grid(row=8, column=0, columnspan=2, pady=(0, 10))

    # build main screen
    def build_main_screen(self, parent):
        center_frame = Frame(parent)
        center_frame.pack(expand=True)

        # title
        Label(
            center_frame,
            text="Ravelry Project Scraper",
            font=(FONT_NAME, FONT_TITLE_SIZE, FONT_STYLE),
        ).grid(row=0, column=0, columnspan=3, pady=(0, 5))

        Label(
            center_frame,
            text=f"Logged in as: {self.username}",
            font=(FONT_NAME, FONT_BODY_SIZE, FONT_STYLE),
        ).grid(row=1, column=0, columnspan=3, pady=(0, 20))

        # form fields, the default values are using agnete cardigan by PetiteKnit, but can type in the pattern slug in the GUI
        # pattern slug is in the URL
        # example: (https://www.ravelry.com/patterns/library/agnete-cardigan) - pattern slug is "agnete-cardigan"
        Label(center_frame, text="Pattern Slug", font=(FONT_NAME, FONT_BODY_SIZE, FONT_STYLE)).grid(
            row=2, column=0, sticky="e", padx=(0, 10), pady=8
        )
        pattern_entry = Entry(center_frame, width=34)
        pattern_entry.insert(0, "agnete-cardigan")
        pattern_entry.grid(row=2, column=1, pady=8)

        Label(center_frame, text="Train CSV", font=(FONT_NAME, FONT_BODY_SIZE, FONT_STYLE)).grid(
            row=5, column=0, sticky="e", padx=(0, 10), pady=8
        )
        train_csv_entry = Entry(center_frame, width=34)
        train_csv_entry.insert(0, "train.csv")
        train_csv_entry.grid(row=5, column=1, pady=8)

        # mode radio buttons
        Label(center_frame, text="Mode", font=(FONT_NAME, FONT_BODY_SIZE, FONT_STYLE)).grid(
            row=6, column=0, sticky="e", padx=(0, 10), pady=(8, 0)
        )
        mode_var = IntVar(value=MODE_BOTH)
        Radiobutton(center_frame, text="Scrape only", variable=mode_var, value=MODE_SCRAPE).grid(
            row=6, column=1, sticky="w"
        )
        Radiobutton(center_frame, text="Sentiment only", variable=mode_var, value=MODE_SENTIMENT).grid(
            row=7, column=1, sticky="w"
        )
        Radiobutton(center_frame, text="Scrape + Sentiment", variable=mode_var, value=MODE_BOTH).grid(
            row=8, column=1, sticky="w", pady=(0, 8)
        )

        # status
        status_label = Label(
            center_frame,
            text="Status: Ready.",
            font=(FONT_NAME, FONT_BODY_SIZE, FONT_STYLE),
            wraplength=380,
            justify="left",
        )
        status_label.grid(row=9, column=0, columnspan=3, pady=(10, 20))

        # buttons
        widgets = {
            "pattern_entry": pattern_entry,
            "excel_entry": excel_entry,
            "predictions_entry": predictions_entry,
            "train_csv_entry": train_csv_entry,
            "mode_var": mode_var,
            "status_label": status_label,
        }

        submit_button = Button(
            center_frame,
            text="Submit",
            width=20,
            bg="brown",
            fg="white",
            command=lambda: self.handle_submit(submit_button, widgets),
        )
        submit_button.grid(row=10, column=0, columnspan=3, pady=8)

        Button(
            center_frame,
            text="Clear All",
            command=lambda: self.clear_main_form(
                pattern_entry, excel_entry, predictions_entry,
                train_csv_entry, mode_var, status_label,
            ),
        ).grid(row=2, column=2, padx=(10, 0))

        Button(
            center_frame,
            text="Log Out",
            command=self.show_login_screen,
        ).grid(row=11, column=0, columnspan=3, pady=(0, 10))

    # load credentials
    def load_credentials_into_form(self, username_entry, password_entry, key_entry, status_label):
        try:
            config_key = key_entry.get().strip() or None
            username, password = load_credentials_from_file(key=config_key)
            username_entry.delete(0, END)
            username_entry.insert(0, username)
            password_entry.delete(0, END)
            password_entry.insert(0, password)
            status_label.config(text="Status: Loaded saved credentials.")
        except Exception as error:
            messagebox.showerror("Error", str(error))

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
                self.window.after(0, lambda: messagebox.showerror("Login Failed", str(error)))
                self.window.after(
                    0,
                    lambda: status_label.config(text=f"Status: Login failed. {error}"),
                )
                self.window.after(0, lambda: login_button.config(state="normal"))

        threading.Thread(target=worker, daemon=True).start()

    # clear typed entries from the form
    def clear_main_form(
        self,
        pattern_entry,
        excel_entry,
        predictions_entry,
        train_csv_entry,
        mode_var,
        status_label,
    ):
        pattern_entry.delete(0, END)
        pattern_entry.insert(0, "agnete-cardigan")
        excel_entry.delete(0, END)
        excel_entry.insert(0, "Agnete-Cardigan.xlsx")
        predictions_entry.delete(0, END)
        predictions_entry.insert(0, "predictions.xlsx")
        train_csv_entry.delete(0, END)
        train_csv_entry.insert(0, "train.csv")
        mode_var.set(MODE_BOTH)
        status_label.config(text="Status: Ready.")

    # handle submit
    def handle_submit(self, submit_button, widgets):
        pattern_slug = widgets["pattern_entry"].get().strip()
        excel_path = widgets["excel_entry"].get().strip()
        predictions_path = widgets["predictions_entry"].get().strip()
        train_csv_path = widgets["train_csv_entry"].get().strip()
        mode = widgets["mode_var"].get()
        status_label = widgets["status_label"]

        if not pattern_slug and mode in {MODE_SCRAPE, MODE_BOTH}:
            messagebox.showerror("Missing Input", "Pattern slug is required for scraping.")
            return

        if not excel_path:
            messagebox.showerror("Missing Input", "Excel file name is required.")
            return

        if mode in {MODE_SENTIMENT, MODE_BOTH} and not train_csv_path:
            messagebox.showerror("Missing Input", "Train CSV path is required for sentiment analysis.")
            return

        if mode in {MODE_SENTIMENT, MODE_BOTH} and not predictions_path:
            messagebox.showerror("Missing Input", "Predictions file name is required for sentiment analysis.")
            return

        submit_button.config(state="disabled")
        status_label.config(text="Status: Starting...")

        def progress(message):
            self.window.after(0, lambda: status_label.config(text=f"Status: {message}"))

        def worker():
            try:
                result = run_pipeline(
                    mode=mode,
                    pattern_slug=pattern_slug,
                    username=self.username,
                    session=self.session,
                    excel_path=excel_path,
                    predictions_path=predictions_path,
                    train_csv_path=train_csv_path,
                    on_progress=progress,
                )

                if result["report"]:
                    progress("Done. Sentiment model report printed to console.")
                    print(result["report"])
                else:
                    progress("Done.")
            except Exception as error:
                self.window.after(0, lambda: messagebox.showerror("Error", str(error)))
                self.window.after(0, lambda: status_label.config(text=f"Status: Error: {error}"))
            finally:
                self.window.after(0, lambda: submit_button.config(state="normal"))

        threading.Thread(target=worker, daemon=True).start()

    def run(self):
        self.window.mainloop()


def main():
    RavelryApp().run()

if __name__ == "__main__":
    main()
