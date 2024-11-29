import os
from typing import Tuple

from flask import current_app
from werkzeug.datastructures import FileStorage

from app.services.logos.exceptions import InvalidContentTypeError, InvalidLogoTypeError, LogoNotFoundError, LogoServiceException

__VALID_CONTENT_TYPE = {"image/jpg", "image/jpeg", "image/png"}

__members_path = None
__projects_path = None
__workshops_path = None


def init_app(app):
    global __members_path, __projects_path, __workshops_path
    static_dir = app.config["STATIC_DIR"].rstrip("/")
    __members_path = static_dir + "/users"
    __projects_path = static_dir + "/projects"
    __workshops_path = static_dir + "/workshops"
    if not os.path.exists(__members_path):
        os.makedirs(__members_path)
    if not os.path.exists(__projects_path):
        os.makedirs(__projects_path)
    if not os.path.exists(__workshops_path):
        os.makedirs(__workshops_path)


def save_logo(resource_id: str, f: FileStorage, logo_type: str) -> None:
    """
    Validates the content type of the provided file and saves it
    to the file system with a filename based on the user or project identifiers and
    the file extension.

    :param username: The resource identifier associated with the logo.
    :type username: str
    :param f: The file storage object representing the uploaded logo.
    :type f: FileStorage
    :param logo_type: Type of the logo, either "members" or "projects".
    :type logo_type: str

    :raises InvalidLogoTypeError: If the  logo_type is not either "members" or "projects".
    :raises LogoServiceException: If an internal error occurs while saving to the filesystem.

    :returns: None
    :rtype: None
    """
    if f.content_type is None:
        raise InvalidContentTypeError("none")

    content_type = f.content_type.split(";")[0]  # e.g. text/plain; charset... | image/jpeg; ...
    if content_type not in __VALID_CONTENT_TYPE:
        raise InvalidContentTypeError(content_type)

    file_ext = content_type.split("/")[1]
    try:
        with open(f"{_get_logo_directory(logo_type)}/{resource_id}.{file_ext}", "wb+") as fp:
            f.save(fp)
    except Exception:
        current_app.debug("save_logo: exception: {e}")
        raise LogoServiceException("Failed saving logo")


def get_logo(resource_id: str, logo_type: str) -> Tuple[str, str]:
    """
    Returns the path to the user or project identifier logo and its mimetype.

    Checks for the existence of a logo file for the resource.
    If found, it returns the path to the logo and its content type.

    :param username: The identifier of the resource associated with the logo.
    :type username: str

    :raises LogoNotFoundError: If no logo file is found for the specified resource.
    :raises InvalidLogoTypeError: If the  logo_type is not either "members" or "projects".

    :returns: A tuple containing the path to the user's logo and its mimetype.
    :rtype: tuple[str, str]
    """
    for content_type in __VALID_CONTENT_TYPE:
        path = f"{_get_logo_directory(logo_type)}/{resource_id}.{content_type.split('/')[1]}"
        if os.path.isfile(path):
            return path, content_type

    raise LogoNotFoundError(resource_id)


def remove_logo(resource_id: str, logo_type: str) -> str:
    for content_type in __VALID_CONTENT_TYPE:
        path = f"{_get_logo_directory(logo_type)}/{resource_id}.{content_type.split('/')[1]}"
        if os.path.isfile(path):
            os.remove(path)
            return resource_id

    raise LogoNotFoundError(resource_id)


def _get_logo_directory(logo_type: str) -> str | None:
    if logo_type == "user":
        return __members_path
    elif logo_type == "project":
        return __projects_path
    elif logo_type == "workshop":
        return __workshops_path
    else:
        raise InvalidLogoTypeError(logo_type=logo_type)
