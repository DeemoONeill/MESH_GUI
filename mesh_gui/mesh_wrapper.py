import shutil
import os
import PySimpleGUI as sg


class MeshSender:
    def __init__(
        self, workflowID, recipient, sender, filenames, subject=None, localID=None
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
        for path in self.filenames:
            file = os.path.split(path)[-1]
            data_file = f"{file}.dat"

            filename = shutil.copy2(path, os.path.join(dest_folder, data_file))
            with open(os.path.join(dest_folder, f"{file}.ctl"), "w") as f:
                f.write(self.generate_ctl())
            return filename


def event_loop(layout):
    window = sg.Window(title="outbox", layout=layout, resizable=True)

    vals = {}
    while True:
        event, values = window.read()
        window["error_text"].update("")
        vals.update(values)
        match event:
            case sg.WIN_CLOSED:
                break
            case "browse":
                file_names = sg.filedialog.askopenfilenames()
                window["filenames"].update(file_names)
            case "send":
                try:
                    MeshSender(**vals).send_file("test_folders/mailbox/out")
                except:
                    print(window.element_list())
                    window["error_text"].update("Missing fields marked with an *")
            case _:
                pass
        print(event, vals)
    window.close()


def main():
    layout = [
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
    event_loop(layout=layout)


if __name__ == "__main__":
    main()
