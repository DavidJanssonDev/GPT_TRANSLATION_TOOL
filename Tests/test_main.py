from main import MainProject

def test_mainproject_init():
    project = MainProject("requirements.txt")
    assert isinstance(project, MainProject)
