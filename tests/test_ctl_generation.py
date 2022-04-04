from .fixtures import mesh_sender, set_up_test_files
import xml.etree.ElementTree as ET
from io import StringIO


def test_ctl_generation(set_up_test_files, mesh_sender):
    etree = ET.parse(StringIO(mesh_sender.generate_ctl()))
    assert etree.getroot().find("WorkflowId").text == "workflow"
