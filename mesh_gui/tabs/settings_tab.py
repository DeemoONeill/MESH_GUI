import mailbox
import os
from tkinter import BROWSE
import PySimpleGUI as sg
import json


class Settings:
    location = os.getenv("APPDATA", "~/.local/share/")
    folder = ".MESHGUI"
    settings_path = os.path.join(location, folder)
    filename = "mesh_gui_settings.json"
    __mailbox_root = None
    __mailbox_id = None

    @property
    def mailbox_root(self):
        return self.__mailbox_root

    @mailbox_root.setter
    def mailbox_root(self, directory):
        self.__mailbox_root = directory
        self.main_window.mailbox_root = directory

    @property
    def mailbox_id(self):
        return self.__mailbox_id

    @mailbox_id.setter
    def mailbox_id(self, mailbox_id):
        self.__mailbox_id = mailbox_id
        self.window["sender"].update(self.mailbox_id)

    def __init__(self, window, main_window) -> None:
        self.main_window = main_window
        self.window = window
        self.load(window)

    def loop(self, event, values, window):

        match event:

            case "Save" | "__TIMEOUT__":
                self.save(values, window)
            case "HelpMeshFolder":
                self.help_mesh_folder()
            case "HelpMailboxID":
                self.help_mailbox()
            case "Load":
                self.load(window)
            case "mailbox_browse":
                self.browse(window)

    def help_mailbox(self):
        sg.popup(
            "The mailbox ID you will typically be sending data from.\n"
            "This is usually your organisations ODS code followed by some digits\nSuch as 24EOT001",
            title="Mailbox ID",
        )

    def browse(self, window):
        filepath = sg.filedialog.askdirectory()
        if filepath:
            window["mailbox_root"].update(filepath)

    def load(self, window):
        try:
            with open(os.path.join(self.settings_path, self.filename), "r") as f:
                values: dict = json.load(f)
            for key, value in values.items():
                window[key].update(value)
            self.mailbox_root = values.get("mailbox_root")
            self.mailbox_id = values.get("Mailbox_ID")
            window["sender"].update(self.mailbox_id)
        except FileNotFoundError:
            return None

    def save(self, values, window):
        self.mailbox_root = values.get("mailbox_root")
        self.mailbox_id = values.get("Mailbox_ID")
        os.makedirs(self.settings_path, exist_ok=True)
        with open(os.path.join(self.settings_path, self.filename), "w") as f:
            json.dump(values, f, default=str)

    def help_mesh_folder(self):
        sg.popup(
            "The location on your machine or network where your mailbox is.\n"
            "By default this will be MESH-DATA-HOME and the mailbox will be MAILBOX01",
            title="Mailbox folder",
        )

    @property
    def mb_root(self):
        return self.mailbox_root

    @staticmethod
    def generate_settings_layout():
        return [
            [sg.T("Settings")],
            [
                sg.T("Mailbox Folder:\t"),
                sg.Input(key="mailbox_root"),
                sg.B(
                    "Browse",
                    enable_events=True,
                    key="mailbox_browse",
                ),
                sg.Help(key="HelpMeshFolder"),
            ],
            [
                sg.T("Your Mailbox ID:\t"),
                sg.Input(key="Mailbox_ID"),
                sg.Help(key="HelpMailboxID"),
            ],
            [sg.VPush()],
            [sg.Button("Save")],
        ]
