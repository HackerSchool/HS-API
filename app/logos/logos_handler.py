# Description: This file contains the class that handles users and projects.
import os

from flask import Flask
from werkzeug.datastructures import FileStorage

from app.logos.exceptions import InvalidContentTypeError, LogoNotFoundError, InvalidLogoTypeError

_VALID_CONTENT_TYPE = {"image/jpg", "image/jpeg", "image/png"}

def _is_valid_content_type(content_type: str) -> bool:
    return content_type in _VALID_CONTENT_TYPE

class LogosHandler:
    def __init__(self):
        self.members_path  = None
        self.projects_path = None

    def save_logo(self, resource_id: str, f: FileStorage, logo_type: str) -> None:
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

        :raises InvalidContentTypeError: If the content type of the uploaded 
        file is not valid.
        :raises InvalidLogoTypeError: If the  logo_type is not either "members" or "projects".

        :returns: None
        :rtype: None
        """
        if f.content_type is None:
            raise InvalidContentTypeError("None")

        content_type = f.content_type.split(";")[0] # e.g. text/plain; charset... | image/jpeg; ...
        if not _is_valid_content_type(content_type):
            raise InvalidContentTypeError(content_type)

        file_ext = content_type.split("/")[1]
        with open(f"{self._get_logo_directory(logo_type)}/{resource_id}.{file_ext}", 'wb+') as fp:
            f.save(fp)

    def get_logo(self, resource_id: str, logo_type: str) -> tuple[str, str]:
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
        for content_type in _VALID_CONTENT_TYPE:
            path = f"{self._get_logo_directory(logo_type)}/{resource_id}.{content_type.split('/')[1]}"
            if os.path.isfile(path):
                return path, content_type
        raise LogoNotFoundError(resource_id)
    
    def remove_logo(self, resource_id: str, logo_type: str):
        for content_type in _VALID_CONTENT_TYPE:
            path = f"{self._get_logo_directory(logo_type)}/{resource_id}.{content_type.split('/')[1]}"
            if os.path.isfile(path):
                os.remove(path)
                return resource_id
 
        return None

    def _get_logo_directory(self, logo_type: str) -> str:
        if logo_type == 'member':
            return self.members_path
        elif logo_type == 'project':
            return self.projects_path
        else:
            raise InvalidLogoTypeError(logo_type)

    def init_app(self, app: Flask) -> None:
        static_dir         = app.config["STATIC_DIR"].rstrip("/")
        self.members_path  = static_dir+"/members"
        self.projects_path = static_dir+"/projects"
        if not os.path.exists(self.members_path):
            os.makedirs(self.members_path)
        if not os.path.exists(self.projects_path):
            os.makedirs(self.projects_path)
 
 