import pytest
import os
from mesh_gui.tabs.send_files import MeshSender


@pytest.fixture(scope="session")
def set_up_test_files():
    tld = "test_folders"
    mailbox = "mailbox"
    mb_folders = ["in", "out", "sent", "failed", "temp"]
    data_folder = "data"

    for folder in mb_folders:
        try:
            os.makedirs(os.path.join(tld, mailbox, folder))
        except OSError:
            pass

    data_dir = os.path.join(tld, data_folder)
    os.makedirs(data_dir, exist_ok=True)
    with open(os.path.join(data_dir, "sample.csv"), "w") as f:
        f.write("1,2,3,4,5")
    yield

    for folder in mb_folders:
        dir = os.path.join(tld, mailbox, folder)
        for file in os.listdir(dir):
            os.remove(os.path.join(dir, file))


@pytest.fixture
def mesh_sender():
    return MeshSender(
        "workflow", "recipient", "sender", ("test_folders/data/sample.csv",)
    )
