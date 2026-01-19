# encoding=utf-8
import os
import tempfile
from urllib.parse import urlparse


def get_object_name_from_aliyun_url(url: str) -> str:
    """Extract the object name from a public Aliyun OSS URL."""
    parsed_url = urlparse(url)
    return parsed_url.path.lstrip("/")


def get_save_tempfile(file_name: str) -> str:
    """Create a temp file path for storing converted docs."""
    temp = tempfile.mkdtemp()
    file_name = os.path.basename(file_name)
    return os.path.join(temp, file_name)
