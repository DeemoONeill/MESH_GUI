from .fixtures import mesh_sender, set_up_test_files
import os


def test_send_file(set_up_test_files, mesh_sender):
    dir = "test_folders/mailbox/out"
    assert mesh_sender.send_file(dir) == r"test_folders/mailbox/out\sample.csv.dat"
    assert len(os.listdir(dir)) == 2
    extensions = [os.path.splitext(file)[-1] for file in os.listdir(dir)]
    assert ".dat" in extensions and ".ctl" in extensions
