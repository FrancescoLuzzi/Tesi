from components.Exceptions import FileTypeException
import os


def check_file_type(file_name: str) -> str:
    """Check if file_name's extension is compatible with images of videos.\n
    If both are false FileTypeException is raised"""
    img_fm = (
        ".tif",
        ".tiff",
        ".jpg",
        ".jpeg",
        ".gif",
        ".png",
        ".eps",
        ".raw",
        ".cr2",
        ".nef",
        ".orf",
        ".sr2",
        ".bmp",
        ".ppm",
        ".heif",
    )
    vid_fm = (".flv", ".avi", ".mp4", ".3gp", ".mov", ".webm", ".ogg", ".qt", ".avchd")
    _, ext = os.path.splitext(file_name)
    if ext in img_fm:
        return "image"
    elif ext in vid_fm:
        return "video"
    else:
        raise FileTypeException
