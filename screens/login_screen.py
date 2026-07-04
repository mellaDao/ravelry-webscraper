import tkinter as tk
from tkinter import END, Button, Entry, Frame, Label

FONT_NAME = "Segoe UI"
FONT_TITLE_SIZE = 20
FONT_BODY_SIZE = 12
FONT_STYLE = ""

class LoginScreen:
    def __init__(self, parent, on_login, on_load_credentials):
        self.on_login = on_login
        self.on_load_credentials = on_load_credentials
        self.build(parent)

    # build login screen
    def build(self, parent):
        center_frame = Frame(parent)
        center_frame.pack(expand=True)

        Label(
            center_frame,
            text="Ravelry Login",
            font=(FONT_NAME, FONT_TITLE_SIZE, FONT_STYLE),
        ).grid(row=0, column=0, columnspan=2, pady=(0, 30))

        # form fields
        Label(center_frame, text="Username", font=(FONT_NAME, FONT_BODY_SIZE, FONT_STYLE)).grid(
            row=1, column=0, sticky="e", padx=(0, 10), pady=8
        )
        self.username_entry = Entry(center_frame, width=30)
        self.username_entry.grid(row=1, column=1, pady=8)

        Label(center_frame, text="Password", font=(FONT_NAME, FONT_BODY_SIZE, FONT_STYLE)).grid(
            row=2, column=0, sticky="e", padx=(0, 10), pady=8
        )
        self.password_entry = Entry(center_frame, width=30, show="*")
        self.password_entry.grid(row=2, column=1, pady=8)

        Label(center_frame, text="Config Key", font=(FONT_NAME, FONT_BODY_SIZE, FONT_STYLE)).grid(
            row=3, column=0, sticky="e", padx=(0, 10), pady=8
        )
        self.key_entry = Entry(center_frame, width=30, show="*")
        self.key_entry.grid(row=3, column=1, pady=8)

        # buttons
        Button(
            center_frame,
            text="Load Saved Credentials",
            command=self._on_load_credentials_clicked,
        ).grid(row=4, column=0, columnspan=2, pady=(20, 8))

        self.login_button = Button(
            center_frame,
            text="Login",
            width=20,
            bg="brown",
            fg="white",
            command=self._on_login_clicked,
        )
        self.login_button.grid(row=5, column=0, columnspan=2, pady=8)

        # status
        self.status_label = Label(
            center_frame,
            text="Status: Enter credentials to log in.",
            font=(FONT_NAME, FONT_BODY_SIZE, FONT_STYLE),
            wraplength=380,
            justify="left",
        )
        self.status_label.grid(row=6, column=0, columnspan=2, pady=(20, 8))

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

    def _on_login_clicked(self):
        self.on_login(
            self.username_entry,
            self.password_entry,
            self.login_button,
            self.status_label,
        )

    def _on_load_credentials_clicked(self):
        self.on_load_credentials(
            self.username_entry,
            self.password_entry,
            self.key_entry,
            self.status_label,
        )