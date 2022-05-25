import os
import datetime
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
    sorted_on = None
    reverse = False

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
        match event, values:
            case self.box_refresh | "__TIMEOUT__", _:
                self.update_tab(window, values)
            case self.box_dir, _:
                self.open_folder()
            case self.table_name, {self.table_name: [row]} if row is not None:
                self.open_file(row, window)
            case self.table_name, {self.table_name: row} if not row:
                self.sort(self.sorted_on, window)
            case (self.table_name, "+CLICKED+", (row, column)), _ if row == -1:
                self.sort(column, window)
            case "Save As", {self.table_name: row} if row:
                self.save_as(row)
            case "Delete", {self.table_name: rows} if rows:
                self.delete(rows, window, values)

    def save_as(self, row):
        if not row:
            return
        filename = self.inbox[row[0]][-2]
        file = sg.filedialog.asksaveasfile(
            "w",
            title="Save as",
            filetypes=self.filetypes,
            defaultextension="*.*",
        )
        if file:
            with file as f:
                with open(os.path.join(self.dir, filename)) as dat:
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
        if self.init and length > self.count:
            if values.get(self.checkbox):
                self.notify(length - self.count)
            self.__update(window, inbox, length)
        elif self.init and length < self.count:
            self.__update(window, inbox, length)
        if not self.init:
            self.__update(window, inbox, length)
            self.init = True

    def __update(self, window, inbox, length):
        window[self.table_name].update(values=inbox)
        window[self.tab].update(f"{self.boxname.capitalize()} ({length})")
        self.count = length
        self.inbox = inbox

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
        unique_files = {os.path.splitext(file)[0] for file in files if os.path.splitext(file)[1].lower() in ".ctl"}
        for file in unique_files:
            file_info = []
            try:
                with open(os.path.join(self.path, f"{file}.ctl")) as f:
                    root = ET.parse(f).getroot().iter()
                    keys = [
                        "DateTime",
                        "From_DTS",
                        "To_DTS",
                        "Subject",
                        "WorkflowId",
                        "LocalId",
                    ]
                    temp_dict = {}
                    for element in root:
                        if (key := element.tag) in keys:
                            text = str(element.text)
                            if key != "DateTime":
                                temp_dict[key] = text
                            elif text:
                                temp_dict[key] = datetime.datetime.strptime(
                                    text, "%Y%m%d%H%M%S"
                                )
                    for key in keys:
                        file_info.append(str(temp_dict.get(key)))
                if (filename := f"{file}.dat") in files:
                    file_info.append(filename)
                else:
                    file_info.append("None")
                file_info.append(f"{file}.ctl")
            except FileNotFoundError:
                pass
            info.append(file_info)
        if not self.sorted_on:
            info = sorted(info)
        return info

    @property
    def dir(self):
        return self.path

    @dir.setter
    def dir(self, directory):
        if directory:
            path = os.path.join(directory, self.folder)
            self.path = os.path.normpath(path)

    def open_file(self, row: int, window: sg.Window):
        if row is not None and (filename := self.inbox[row][-2]) != "None":
            subprocess.Popen(
                f"notepad {os.path.join(self.path,filename)}",
            )

    def delete(self, rows, window, values):
        if self.delete_prompt(len(rows)):
            for row in rows:
                try:
                    current = self.inbox[row]
                    files = current[-2], current[-1]
                    for file in files:
                        if file == "None":
                            continue
                        try:
                            os.remove(os.path.join(self.path, file))
                        except FileNotFoundError:
                            continue
                except PermissionError:
                    sg.popup_notify("I don't have permission to remove these files")
            self.update_tab(window, values)

    def delete_prompt(self, num):
        choice, _ = sg.Window(
            "Continue?",
            [
                [
                    sg.T(
                        f"Are you sure you want to delete {num} file{'s' if num>1 else ''}"
                    )
                ],
                [sg.Yes(s=10), sg.No(s=10)],
            ],
            disable_close=True,
        ).read(close=True)
        return choice == "Yes"

    def sort(self, column, window):
        if self.sorted_on == column:
            self.reverse = not self.reverse
        else:
            self.reverse = False
            self.sorted_on = column

        self.inbox = sorted(self.inbox, key=lambda x: x[column], reverse=self.reverse)
        self.sorted_on = column
        self.__update(window, self.inbox, len(self.inbox))


def generate_box_layout(boxname: str):
    return [
        [sg.T(f"MESH {boxname}")],
        [
            sg.Table(
                [[]],
                headings=[
                    "Time",
                    "From",
                    "To",
                    "Subject",
                    "WorkflowID",
                    "LocalID",
                    "Filename",
                ],
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
                # right_click_selects=True,
                enable_click_events=True,
            )
        ],
        [
            sg.B(f"Refresh", key=f"{boxname}_refresh"),
            sg.Checkbox("Allow Notifications?", key=f"{boxname}_checkbox"),
            sg.Push(),
            sg.B("Open Folder location", key=f"{boxname}_dir"),
        ],
    ]
