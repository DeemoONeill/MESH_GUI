import PySimpleGUI as sg
import tabs.send_files as send_files
import tabs.inbox as inbox


def event_loop(layout):
    window = sg.Window(title="MESH", layout=layout, resizable=True)
    file_sender = send_files.Send_Files()
    boxes = dict(
        INBOX_TAB=inbox.Mesh_box("inbox", "test_folders/mailbox/in"),
        OUTBOX_TAB=inbox.Mesh_box("outbox", "test_folders/mailbox/out"),
        SENT_TAB=inbox.Mesh_box("sent", "test_folders/mailbox/sent"),
    )
    while True:
        event, values = window.read(timeout=10000)
        for box in boxes.values():
            box.update_inbox_tab(window)
        window["error_text"].update("")
        match event, values:
            case sg.WIN_CLOSED, _:
                break

            case _, {"-tabs-": "Send Message"}:
                file_sender.loop(event=event, values=values, window=window)

            case _, {"-tabs-": tabname}:
                boxes[tabname].loop(event, values, window)

            case "__TIMEOUT__", _:
                for box in boxes.values():
                    box.loop(event, values, window)

        print(event, values)
    window.close()


def generate_boxes():
    for name in ["Inbox", "Outbox", "Sent"]:
        yield sg.Tab(
            name,
            inbox.generate_box_layout(name.lower()),
            key=f"{name.upper()}_TAB",
            expand_x=True,
            expand_y=True,
        )


def main():

    layout = [
        [
            sg.TabGroup(
                [
                    [
                        sg.Tab(
                            "Send Message",
                            send_files.SEND_MESSAGE_LAYOUT,
                            expand_x=True,
                            expand_y=True,
                        ),
                        *generate_boxes(),
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
    ]
    event_loop(layout=layout)


if __name__ == "__main__":
    main()
