# Description: This file contains the class that handles the logos of the companies.
import os

from flask import Flask

class LogosHandler:
    def __init__(self):
        self.folder_path = None 

    def init_app(self, app: Flask) -> None:
        self.folder_path = app.config["LOGOS_PATH"]
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)

    def getLogo(self, name: str) -> bytes:
        try:
            with open(f"{self.folder_path}/{name}.png", 'rb') as file:
                return file.read()
        except FileNotFoundError:
            return None
        
    def writeLogo(self, name: str, data: bytes) -> bool:
        with open(f"{self.folder_path}/{name}.png", 'wb') as file:
            file.write(data)
        return True
