import os
import shutil
import pytest
from mesh_gui.tabs import inbox as box
import unittest.mock as mock
from dataclasses import dataclass


class MockPopup:
    title = None
    content = None

    def __call__(self, content, title):
        self.content = content
        self.title = title


class MockPopen:
    args = None

    def __call__(self, args):
        self.args = args


def test_init():
    inb = box.Mesh_box("inbox", "in")
    assert inb.dir == None
    assert inb.box_refresh == "inbox_refresh"
    assert inb.table_name == "inboxtable"
    assert inb.tab == "INBOX_TAB"
    assert inb.box_dir == "inbox_dir"
    assert inb.checkbox == "inbox_checkbox"


@pytest.fixture
def inbox(filename):
    inb = box.Mesh_box("inbox", "in")
    inb.inbox = [[filename]]
    return inb


def test_dir_set(inbox: box.Mesh_box):
    assert inbox.path == None
    inbox.dir = "test_folders/mailbox"
    assert inbox.path == r"test_folders\mailbox\in"


@pytest.fixture
def inbox_path(inbox):
    inbox.dir = "test_folders/mailbox"
    return inbox


@pytest.fixture
def filename():
    return "filename.txt"


@pytest.fixture
def test_file(filename):
    file_path = os.path.join("test_folders/mailbox/in", filename)
    with open(file_path, "w") as f:
        f.write("file contents")
    yield
    os.remove(file_path)


@pytest.fixture
def folders(filename):
    directory = "test/folder"
    os.makedirs(directory, exist_ok=True)
    yield directory
    shutil.rmtree(directory)


@pytest.fixture
def return_file(folders):
    with open(os.path.join(folders, "file.txt"), "w") as f:
        yield f


def test_saveas(inbox_path: box.Mesh_box, folders, return_file, test_file):
    with mock.patch(
        "PySimpleGUI.filedialog.asksaveasfile",
        return_value=return_file,
    ):
        row = [0]
        inbox_path.save_as(row)


def test_open_folder(inbox_path):
    with (
        mock.patch("PySimpleGUI.popup", new_callable=MockPopup) as mocked,
        mock.patch("subprocess.Popen", new_callable=MockPopen) as subprocess,
    ):
        inbox_path.open_folder()
        assert mocked.title == "Info"
        assert "explorer" in subprocess.args
        explorer, path = subprocess.args.split(" ")
        assert path == inbox_path.path
