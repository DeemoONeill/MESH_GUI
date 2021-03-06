import os
import shutil
import PySimpleGUI as sg


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
            raise ValueError("Missing fields marked with *")
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


class Send_Files:
    filenames = set()

    def loop(self, event, values, window):

        match event:
            case "browse":
                self.filenames = self.filenames | set(sg.filedialog.askopenfilenames())
                window["filenames"].update(sorted(self.filenames))

            case "remove":
                self.filenames = self.filenames - set(values["filenames"])
                window["filenames"].update(sorted(self.filenames))

            case "send":
                try:
                    values["filenames"] = self.filenames
                    sent = MeshSender(**values).send_file(self.dir)
                    window["success_text"].update(
                        f"{len(self.filenames)} File{'s' if len(self.filenames)>1 else ''} added to outbox"
                    )
                    window["filenames"].update([])
                    self.filenames = set()
                except Exception as e:
                    window["error_text"].update(e)

    @property
    def dir(self):
        return self.__dir

    @dir.setter
    def dir(self, directory):
        print(directory)
        dir = os.path.join(directory, "out/")
        self.__dir = os.path.normpath(dir)


def generate_send_message_layout():
    return [
        [sg.T("Send Message")],
        [
            sg.T("From:*\t\t"),
            sg.Input(
                key="sender",
                tooltip="Your Mailbox ID",
                readonly=True,
                disabled_readonly_background_color="light grey",
                focus=False,
            ),
        ],
        [
            sg.T("To:*\t\t"),
            sg.I(key="recipient", tooltip="Recipients Mailbox ID"),
        ],
        [
            sg.T("WorkflowID:*\t"),
            sg.I(key="workflowID", tooltip="The workflow ID for the data collection"),
        ],
        [
            sg.T("Subject:\t\t"),
            sg.Input(
                key="subject",
                tooltip="Message Subject, see collection information for details",
            ),
        ],
        [sg.T("LocalID:\t\t"), sg.Input(key="localID")],
        [
            sg.T("Data file(s)*\t"),
            sg.B(
                "Browse",
                tooltip="hold shift and click to select multiple files",
                key="browse",
            ),
        ],
        [
            sg.Listbox(
                values=[], size=(60, 4), key="filenames", expand_x=True, expand_y=True
            )
        ],
        [sg.B("Remove", key="remove", tooltip="Removes selected file")],
        [sg.HorizontalSeparator()],
        [sg.B("Send", key="send")],
        [sg.T(text_color="red", key="error_text"), sg.T(key="success_text")],
    ]
