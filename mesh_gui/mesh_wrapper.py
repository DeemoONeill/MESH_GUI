import shutil
import os
import PySimpleGUI as sg
import xml.etree.ElementTree as ET
import tabs.send_files as send_files
import tabs.inbox as inbox


def event_loop(layout):
    window = sg.Window(title="MESH", layout=layout, resizable=True)
    file_sender = send_files.Send_Files()
    inbox_ = inbox.Inbox()
    tabs = [file_sender, inbox_]
    while True:
        event, values = window.read(timeout=10000)
        window["error_text"].update("")
        match event, values:
            case sg.WIN_CLOSED, _:
                break

            case _, {"tabs": "Send Message"}:
                file_sender.loop(event=event, values=values, window=window)

            case _, {"tabs": "Inbox"}:
                inbox_.loop(event, values, window)
            case "__TIMEOUT__", _:
                for tab in tabs:
                    tab.loop(event, values, window)
        print(event)
    window.close()


def main():

    layout = [
        [
            sg.TabGroup(
                [
                    [
                        sg.Tab("Send Message", send_files.SEND_MESSAGE_LAYOUT),
                        sg.Tab("Inbox", inbox.INBOX_LAYOUT),
                    ]
                ],
                key="tabs",
            )
        ]
    ]
    event_loop(layout=layout)


if __name__ == "__main__":
    main()
