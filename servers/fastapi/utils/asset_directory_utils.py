import os
from utils.get_env import get_app_data_directory_env


def convert_absolute_path_to_web_path(absolute_path: str) -> str:
    """Convert absolute file path to web-accessible path"""
    app_data_dir = get_app_data_directory_env()
    if app_data_dir and absolute_path.startswith(app_data_dir):
        # Convert /Users/.../app_data/images/xxx.jpg to /app_data/images/xxx.jpg
        relative_path = absolute_path[len(app_data_dir.rstrip('/')):]
        return f"/app_data{relative_path}"
    return absolute_path


def get_images_directory():
    images_directory = os.path.join(get_app_data_directory_env(), "images")
    os.makedirs(images_directory, exist_ok=True)
    return images_directory


def get_exports_directory():
    export_directory = os.path.join(get_app_data_directory_env(), "exports")
    os.makedirs(export_directory, exist_ok=True)
    return export_directory

def get_uploads_directory():
    uploads_directory = os.path.join(get_app_data_directory_env(), "uploads")
    os.makedirs(uploads_directory, exist_ok=True)
    return uploads_directory
