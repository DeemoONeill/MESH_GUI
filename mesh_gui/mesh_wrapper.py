import PySimpleGUI as sg
import tabs.send_files as send_files
import tabs.inbox as inbox
import tabs.settings_tab as settings
import os

here = os.path.split(__file__)[0]


class main_window:
    __mb_root = None

    def event_loop(self, layout):
        window = sg.Window(
            title="MESH Client GUI",
            layout=layout,
            resizable=True,
            scaling=1.5,
            font="normal 11",
        )
        event, values = window.read(timeout=0)
        self.file_sender = send_files.Send_Files()
        self.boxes = dict(
            INBOX_TAB=inbox.Mesh_box("inbox", "in"),
            OUTBOX_TAB=inbox.Mesh_box("outbox", "out"),
            SENT_TAB=inbox.Mesh_box("sent", "sent"),
        )
        self.settings_ = settings.Settings(window, self)
        self.settings_.boxes = self.boxes
        while True:
            for box in self.boxes.values():
                box.update_tab(window, values)
            event, values = window.read(timeout=10000)
            window["error_text"].update("")
            match event, values:
                case sg.WIN_CLOSED, _:
                    break

                case "__TIMEOUT__", _:
                    for box in self.boxes.values():
                        box.loop(event, values, window)
                    self.settings_.loop(event, values, window)

                case _, {"-tabs-": "Send Message"}:
                    self.file_sender.loop(event=event, values=values, window=window)

                case _, {"-tabs-": "Settings"}:
                    self.settings_.loop(event, values, window)

                case _, {"-tabs-": tabname} if tabname in self.boxes:
                    self.boxes[tabname].loop(event, values, window)

            print(event, values)
        window.close()

    @property
    def mailbox_root(self):
        return self.__mb_root

    @mailbox_root.setter
    def mailbox_root(self, directory):
        self.__mb_root = directory
        for box in self.boxes.values():
            box.dir = directory
        self.file_sender.dir = directory

    def generate_boxes(self):
        for name in ["Inbox", "Outbox", "Sent"]:
            yield sg.Tab(
                name,
                inbox.generate_box_layout(name.lower()),
                key=f"{name.upper()}_TAB",
                expand_x=True,
                expand_y=True,
            )

    def main(self):

        layout = [
            [
                sg.TabGroup(
                    [
                        [
                            sg.Tab(
                                "Send Message",
                                send_files.generate_send_message_layout(),
                                expand_x=True,
                                expand_y=True,
                            ),
                            *self.generate_boxes(),
                            sg.Tab(
                                "Settings",
                                settings.Settings.generate_settings_layout(),
                                expand_x=True,
                                expand_y=True,
                            ),
                        ]
                    ],
                    key="-tabs-",
                    enable_events=True,
                    expand_x=True,
                    expand_y=True,
                    tab_location=sg.TAB_LOCATION_TOP_LEFT,
                    size=(1000, 700),
                ),
            ],
            [sg.VPush()],
        ]
        self.event_loop(layout=layout)


if __name__ == "__main__":
    window = main_window()
    window.main()
