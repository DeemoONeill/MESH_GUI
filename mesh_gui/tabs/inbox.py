import os
import time
import xml.etree.ElementTree as ET
import PySimpleGUI as sg
import subprocess

popup = False


class Mesh_box:
    count = 0
    init = False
    inbox: list = None
    filetypes = (
        ("Text Files (.txt)", "*.txt"),
        ("Web Page (.html)", "*.html"),
        ("XML file (.xml)", "*.xml"),
        ("JSON file (.json)", "*.json"),
        ("Comma Separated Variables (.csv)", "*.csv"),
    )
    path = None

    def __init__(self, boxname: str, folder, dir=None):
        self.folder = folder
        self.dir = dir
        if self.dir and self.folder:
            self.path = os.path.join(dir, folder)
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
            case self.table_name:
                row = values.get(self.table_name)
                self.open_file(row, window)
            case "Save As":
                row = values.get(self.table_name)
                self.save_as(row)
            case "Delete":
                row = values.get(self.table_name)[0]
                if row:
                    pass

    def save_as(self, row):
        if not row:
            return
        filename = self.inbox[row[0]][-1]
        file = sg.filedialog.asksaveasfile(
            "w",
            title="Save as",
            filetypes=self.filetypes,
            defaultextension="*.*",
        )
        if file:
            with file as f:
                with open(os.path.join(self.path, filename)) as dat:
                    f.write(dat.read())

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
        subprocess.Popen(f"explorer {os.path.normpath(self.path)}")

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
        if not self.path and self.dir:
            self.path = os.path.join(self.dir, self.folder)
        elif not self.dir:
            return info
        try:
            files = os.listdir(self.path)
        except FileNotFoundError:
            return info
        unique_files = {os.path.splitext(file)[0] for file in files}
        for file in unique_files:
            file_info = []
            try:
                with open(os.path.join(self.path, f"{file}.ctl")) as f:
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

    @property
    def dir(self):
        return self.path

    @dir.setter
    def dir(self, directory):
        if directory:
            path = os.path.join(directory, self.folder)
            self.path = os.path.normpath(path)

    def open_file(self, rows: list, window: sg.Window):
        for r in rows:
            if r is not None and (filename := self.inbox[r][-1]):
                subprocess.Popen(
                    f"notepad {os.path.join(self.path,filename)}",
                )


def generate_box_layout(boxname: str):
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
                bind_return_key=True,
                tooltip="Double click to open file",
                right_click_menu=[
                    "&Right",
                    ["Save As", "Delete"],
                ],
                right_click_selects=True,
            )
        ],
        [
            sg.B(f"Refresh", key=f"{boxname}_refresh"),
            sg.Checkbox("Allow Notifications?", key=f"{boxname}_checkbox"),
            sg.Push(),
            sg.B("Open Folder location", key=f"{boxname}_dir"),
        ],
    ]
