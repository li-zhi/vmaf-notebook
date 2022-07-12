import os

# Path to folder containing this file
VMAF_NOTEBOOK_PYTHON_ROOT = os.path.dirname(os.path.abspath(__file__))

REPO_ROOT = os.path.abspath(os.path.join(VMAF_NOTEBOOK_PYTHON_ROOT, '..', ))


def resource_path(*components):
    return os.path.join(REPO_ROOT, "resource", *components)


def workspace_path(*components):
    return os.path.join(REPO_ROOT, "workspace", *components)


def workdir_path(*components):
    return os.path.join(REPO_ROOT, "workspace", "workdir", *components)


def tests_resource_path(*components):
    return os.path.join(REPO_ROOT, "tests", "resource", *components)


def model_path(*components):
    return os.path.join(VMAF_NOTEBOOK_PYTHON_ROOT, "model", *components)
