import os
import xml.etree.ElementTree as ET
import PySimpleGUI as sg


def check_inbox():
    info = []
    dir = "test_folders/mailbox/in"
    files = os.listdir(dir)
    unique_files = {os.path.splitext(file)[0] for file in files}
    for file in unique_files:
        file_info = []
        try:
            with open(os.path.join(dir, f"{file}.ctl")) as f:
                root = ET.parse(f).getroot()
                for value in ["From_DTS", "To_DTS", "Subject", "WorkflowId"]:
                    file_info.append(root.find(value).text)
        except FileNotFoundError:
            pass
        if (filename := f"{file}.dat") in files:
            file_info.append(filename)
        info.append(file_info)
    return info


class Inbox:
    def loop(self, event, values, window):
        match event:
            case "inbox_refresh" | "__TIMEOUT__":
                inbox = check_inbox()
                window["table"].update(values=inbox)


INBOX_LAYOUT = [
    [sg.Text("MESH Inbox")],
    [
        sg.Table(
            [[]],
            headings=[
                "From",
                "To",
                "Subject",
                "WorkflowID",
                "LocalID",
                "Filename",
                "Save",
                "Delete",
            ],
            key="table",
            auto_size_columns=False,
        )
    ],
    [sg.Button("refresh inbox", key="inbox_refresh")],
]
