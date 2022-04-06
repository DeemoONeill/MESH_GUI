from mesh_gui.tabs.send_files import MeshSender
from .fixtures import mesh_sender, set_up_test_files
import os
import pytest


@pytest.fixture
def test_dir():
    return "test_folders/mailbox/out"


def test_send_single_file(set_up_test_files, mesh_sender, test_dir):
    assert mesh_sender.send_file(test_dir) == [
        r"test_folders/mailbox/out\sample.csv.dat"
    ]
    assert len(os.listdir(test_dir)) == 2
    extensions = [os.path.splitext(file)[-1] for file in os.listdir(test_dir)]
    assert ".dat" in extensions and ".ctl" in extensions


def test_send_two_files(set_up_test_files, mesh_sender, test_dir):
    mesh_sender = MeshSender(
        "workflow",
        "recipient",
        "sender",
        ("test_folders/data/sample.csv", "test_folders/data/sample2.csv"),
    )
    assert mesh_sender.send_file(test_dir) == [
        r"test_folders/mailbox/out\sample.csv.dat",
        r"test_folders/mailbox/out\sample2.csv.dat",
    ]
