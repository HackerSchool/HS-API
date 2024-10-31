import os
# Description: This file contains the class that handles the logos of the companies.

class Logos:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        # Create the folder if it doesn't exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    def getLogo(self, name):
        try:
            with open(f"{self.folder_path}/{name}.png", 'rb') as file:
                return file.read()
        except FileNotFoundError:
            return None
        
    def writeLogo(self, name, data):
        with open(f"{self.folder_path}/{name}.png", 'wb') as file:
            file.write(data)
        return True
