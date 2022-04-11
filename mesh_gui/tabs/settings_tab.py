import os
from turtle import title
import PySimpleGUI as sg


class Settings:
    def loop(self, event, values, window):

        match event:

            case "Save":
                self.save()
            case "HelpMeshFolder":
                self.help_mesh_folder()
            case "HelpMailboxID":
                self.help_mailbox()

    def help_mailbox(self):
        sg.popup(
            "The mailbox ID you will typically be sending data from.\nThis is usually your organisations ODS code followed by some digits\nSuch as 24EOT001",
            title="Mailbox ID",
        )

    def save(self):
        location = os.getenv("APPDATA", "~/.local/share/")
        folder = ".MESHGUI"
        os.makedirs(os.path.join(location, folder))
        filename = "mesh_gui_settings.json"
        with open(os.path.join(location, folder, filename), "w") as f:
            f.write("hello")

    def help_mesh_folder(self):
        sg.popup(
            "The location on your machine or network where your mailbox is.\nBy default this will be MESH-DATA-HOME and the mailbox will be MAILBOX01",
            title="Mailbox folder",
        )

    @staticmethod
    def generate_settings_layout():
        return [
            [sg.T("Settings")],
            [
                sg.T("Mailbox Folder:\t"),
                sg.Input(),
                sg.B(
                    "browse",
                    button_type=sg.BUTTON_TYPE_BROWSE_FOLDER,
                    target=(sg.ThisRow, -1),
                ),
                sg.Help(key="HelpMeshFolder"),
            ],
            [
                sg.T("Your Mailbox ID:\t"),
                sg.Input(),
                sg.Help(key="HelpMailboxID"),
            ],
            [sg.VPush()],
            [sg.Button("Save")],
        ]
