import tkinter as tk
from tkinter import END, Button, Entry, Frame, IntVar, Label, Radiobutton

FONT_NAME = "Segoe UI"
FONT_TITLE_SIZE = 20
FONT_BODY_SIZE = 12
FONT_STYLE = ""

MODE_SCRAPE = 1
MODE_SENTIMENT = 2
MODE_BOTH = 3

class MainScreen:
    def __init__(self, parent, username, on_submit, on_clear, on_logout):
        self.parent = parent
        self.username = username
        self.on_submit = on_submit
        self.on_clear = on_clear
        self.on_logout = on_logout
        self.build(parent)

    # build main screen
    def build(self, parent):
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

        # form fields
        Label(center_frame, text="Pattern Slug", font=(FONT_NAME, FONT_BODY_SIZE, FONT_STYLE)).grid(
            row=2, column=0, sticky="e", padx=(0, 10), pady=8
        )
        self.pattern_entry = Entry(center_frame, width=34)
        self.pattern_entry.insert(0, "agnete-cardigan")
        self.pattern_entry.grid(row=2, column=1, pady=8)

        Label(center_frame, text="Train CSV", font=(FONT_NAME, FONT_BODY_SIZE, FONT_STYLE)).grid(
            row=3, column=0, sticky="e", padx=(0, 10), pady=8
        )
        self.train_csv_entry = Entry(center_frame, width=34)
        self.train_csv_entry.insert(0, "train.csv")
        self.train_csv_entry.grid(row=3, column=1, pady=8)

        # mode radio buttons
        Label(center_frame, text="Mode", font=(FONT_NAME, FONT_BODY_SIZE, FONT_STYLE)).grid(
            row=4, column=0, sticky="e", padx=(0, 10), pady=(8, 0)
        )
        self.mode_var = IntVar(value=MODE_BOTH)
        Radiobutton(center_frame, text="Scrape only", variable=self.mode_var, value=MODE_SCRAPE).grid(
            row=4, column=1, sticky="w"
        )
        Radiobutton(center_frame, text="Sentiment only", variable=self.mode_var, value=MODE_SENTIMENT).grid(
            row=5, column=1, sticky="w"
        )
        Radiobutton(center_frame, text="Scrape + Sentiment", variable=self.mode_var, value=MODE_BOTH).grid(
            row=6, column=1, sticky="w", pady=(0, 8)
        )

        # status
        self.status_label = Label(
            center_frame,
            text="Status: Ready.",
            font=(FONT_NAME, FONT_BODY_SIZE, FONT_STYLE),
            wraplength=380,
            justify="left",
        )
        self.status_label.grid(row=7, column=0, columnspan=3, pady=(10, 20))

        # buttons
        self.submit_button = Button(
            center_frame,
            text="Submit",
            width=20,
            bg="brown",
            fg="white",
            command=self._on_submit_clicked,
        )
        self.submit_button.grid(row=8, column=0, columnspan=3, pady=8)

        Button(
            center_frame,
            text="Clear All",
            command=self.clear_main_form,
        ).grid(row=2, column=2, padx=(10, 0))

        Button(
            center_frame,
            text="Log Out",
            command=self.on_logout,
        ).grid(row=9, column=0, columnspan=3, pady=(0, 10))

    def _on_submit_clicked(self):
        widgets = {
            "pattern_entry": self.pattern_entry,
            "train_csv_entry": self.train_csv_entry,
            "mode_var": self.mode_var,
            "status_label": self.status_label,
            "submit_button": self.submit_button,
        }
        self.on_submit(widgets)

    def clear_main_form(self):
        self.pattern_entry.delete(0, END)
        self.pattern_entry.insert(0, "agnete-cardigan")
        self.train_csv_entry.delete(0, END)
        self.train_csv_entry.insert(0, "train.csv")
        self.mode_var.set(MODE_BOTH)
        self.status_label.config(text="Status: Ready.")