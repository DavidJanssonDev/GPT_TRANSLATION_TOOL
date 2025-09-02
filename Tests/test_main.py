from main import MainProject

def test_mainproject_init():
    project = MainProject()
    assert isinstance(project, MainProject)
