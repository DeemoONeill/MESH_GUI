import os
import time
import xml.etree.ElementTree as ET
import PySimpleGUI as sg
import subprocess

popup = False


class Mesh_box:
    count = 0
    init = False
    last_clicked = None
    inbox: list = None

    def __init__(self, boxname: str, dir):
        self.dir = dir
        self.boxname = boxname
        self.box_refresh = f"{boxname}_refresh"
        self.table_name = f"{boxname}table"
        self.tab = f"{boxname.upper()}_TAB"
        self.box_dir = f"{boxname}_dir"
        self.checkbox = f"{boxname}_checkbox"

    def loop(self, event, values, window):
        match event:
            case self.box_refresh | "__TIMEOUT__":
                self.update_tab(window, values)
            case self.box_dir:
                self.open_folder()
            case (self.table_name, "+CLICKED+", (row, column)):
                self.open_file(row, window)

    def open_folder(self):
        global popup
        if not popup:
            sg.popup(
                "There are two types of files present:\n"
                "A ctl file which contains the routing information, and a dat file which contains the data.\n"
                "We recommend that you move or remove the files with the same names together.",
                title="Info",
            )
            popup = True
        subprocess.Popen(f"explorer {self.dir}")

    def update_tab(self, window, values: dict):
        inbox = self.check_inbox()
        length = len(inbox)
        if values.get(self.checkbox) and self.init and length > self.count:
            self.notify(length - self.count)
        window[self.table_name].update(values=inbox)
        window[self.tab].update(f"{self.boxname.capitalize()} ({length})")
        self.count = length
        self.inbox = inbox
        if not self.init:
            self.init = True

    def notify(self, count):
        sg.popup_notify(
            f"{count} New message{'s' if count>1 else ''} in {self.boxname}",
            title=f"MESH {self.boxname}",
        )

    def check_inbox(self):
        info = []
        files = os.listdir(self.dir)
        unique_files = {os.path.splitext(file)[0] for file in files}
        for file in unique_files:
            file_info = []
            try:
                with open(os.path.join(self.dir, f"{file}.ctl")) as f:
                    root = ET.parse(f).getroot()
                    for value in [
                        "From_DTS",
                        "To_DTS",
                        "Subject",
                        "WorkflowId",
                        "LocalId",
                    ]:
                        file_info.append(root.find(value).text)
            except FileNotFoundError:
                pass
            if (filename := f"{file}.dat") in files:
                file_info.append(filename)
            else:
                file_info.append(None)
            info.append(file_info)

        return info

    def open_file(self, row, window: sg.Window):
        if not self.last_clicked:
            self.last_clicked = time.time()
        else:
            if (time.time() - self.last_clicked) < 0.7:
                if row is not None and (filename := self.inbox[row][-1]):
                    subprocess.Popen(
                        f"notepad {os.path.join(self.dir,filename)}",
                    )
            else:
                self.last_clicked = time.time()


def generate_box_layout(boxname):
    return [
        [sg.T(f"MESH {boxname}")],
        [
            sg.Table(
                [[]],
                headings=["From", "To", "Subject", "WorkflowID", "LocalID", "Filename"],
                key=f"{boxname}table",
                auto_size_columns=True,
                expand_x=True,
                expand_y=True,
                enable_click_events=True,
                tooltip="Double click to open file",
            )
        ],
        [
            sg.B(f"refresh {boxname}", key=f"{boxname}_refresh"),
            sg.Checkbox("Allow Notifications for this box?", key=f"{boxname}_checkbox"),
            sg.Push(),
            sg.B("Open Folder location", key=f"{boxname}_dir"),
        ],
    ]
