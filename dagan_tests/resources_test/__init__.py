import os


def resource_test_path(relative_path):
    """
    Get absolute path to resource

    :param relative_path: Path from this folder
    :return: Absolute path to resource
    """
    return os.path.join(os.path.dirname(__file__), relative_path)
