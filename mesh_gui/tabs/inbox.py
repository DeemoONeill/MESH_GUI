import os
import time
import xml.etree.ElementTree as ET
import PySimpleGUI as sg
import subprocess


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
        self.tab = f"{self.boxname.upper()}_TAB"

    def loop(self, event, values, window):
        match event:
            case self.box_refresh | "__TIMEOUT__":
                self.update_inbox_tab(window)
            case (self.table_name, "+CLICKED+", (row, column)):
                self.open_file(row, window)

    def update_inbox_tab(self, window):
        inbox = self.check_inbox()
        length = len(inbox)
        if self.init and length > self.count:
            self.notify()
        window[self.table_name].update(values=inbox)
        window[self.tab].update(f"{self.boxname.capitalize()} ({length})")
        self.count = length
        self.inbox = inbox

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
            )
        ],
        [sg.B(f"refresh {boxname}", key=f"{boxname}_refresh")],
    ]
