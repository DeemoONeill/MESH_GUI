import shutil
import os
import PySimpleGUI as sg
import xml.etree.ElementTree as ET


class MeshSender:
    def __init__(
        self,
        workflowID,
        recipient,
        sender,
        filenames,
        subject=None,
        localID=None,
        **kwargs,
    ):
        if not workflowID or not recipient or not sender or not filenames:
            raise ValueError("Missing required field")
        self.workflowID = workflowID
        self.recipient = recipient
        self.sender = sender
        self.subject = subject
        self.localID = localID
        self.filenames = filenames

    def generate_ctl(self):
        return f"""<DTSControl>
    <Version>1.0</Version>
    <AddressType>DTS</AddressType>
    <MessageType>Data</MessageType>
    <WorkflowId>{self.workflowID or ""}</WorkflowId>
    <To_DTS>{self.recipient or ""}</To_DTS>
    <From_DTS>{self.sender or ""}</From_DTS>
    <Subject>{self.subject or ""}</Subject>
    <LocalId>{self.localID or ""}</LocalId>
    <Compress>Y</Compress>
    <AllowChunking>Y</AllowChunking>
    <Encrypted>N</Encrypted>
</DTSControl>
        """

    def send_file(self, dest_folder):
        moved_files = []
        for path in self.filenames:
            file = os.path.split(path)[-1]
            data_file = f"{file}.dat"

            moved_files.append(shutil.copy2(path, os.path.join(dest_folder, data_file)))
            with open(os.path.join(dest_folder, f"{file}.ctl"), "w") as f:
                f.write(self.generate_ctl())
        return moved_files


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


def event_loop(layout):
    window = sg.Window(title="MESH", layout=layout, resizable=True)
    filenames = set()
    while True:
        event, values = window.read()
        window["error_text"].update("")
        match event:
            case sg.WIN_CLOSED:
                break
            case "browse":
                filenames = filenames | set(sg.filedialog.askopenfilenames())
                window["filenames"].update(filenames)
            case "send":
                try:
                    values["filenames"] = filenames
                    MeshSender(**values).send_file("test_folders/mailbox/out")
                except:
                    print(window.element_list())
                    window["error_text"].update("Missing fields marked with an *")
            case "inbox_refresh":
                inbox = check_inbox()
                window["table"].update(values=inbox)
            case _:
                pass
    window.close()


def main():
    send_message = [
        [sg.Text("MESH Outbox")],
        [sg.Text("From:*\t\t"), sg.Input(key="sender", tooltip="Your Mailbox ID")],
        [
            sg.Text("To:*\t\t"),
            sg.Input(key="recipient", tooltip="Recipients Mailbox ID"),
        ],
        [
            sg.Text("WorkflowID:*\t"),
            sg.Input(
                key="workflowID", tooltip="The workflow ID for the data collection"
            ),
        ],
        [sg.Text("Subject:\t\t"), sg.Input(key="subject", tooltip="Subject")],
        [sg.Text("LocalID:\t\t"), sg.Input(key="localID")],
        [
            sg.Text("Data file(s)*\t"),
            sg.Button(
                "Browse",
                tooltip="hold shift and click to select multiple files",
                key="browse",
            ),
        ],
        [sg.Listbox(values=[], size=(60, 4), key="filenames")],
        [sg.HorizontalSeparator()],
        [sg.Button("Send", key="send")],
        [sg.Text(text_color="red", key="error_text")],
    ]
    inbox = [
        [sg.Text("MESH Inbox")],
        [
            sg.Table(
                [[]],
                headings=["from", "to", "subject", "workflow", "Filename"],
                key="table",
                auto_size_columns=False,
            )
        ],
        [sg.Button("refresh inbox", key="inbox_refresh")],
    ]
    layout = [
        [
            sg.TabGroup(
                [[sg.Tab("Send Message", send_message), sg.Tab("Inbox", inbox)]],
                key="tabs",
            )
        ]
    ]
    event_loop(layout=layout)


if __name__ == "__main__":
    main()
