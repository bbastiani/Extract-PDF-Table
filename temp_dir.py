import tempfile
import shutil

class TempDir():
    def __init__(self):
        self.path = self.create_tmp_dir()

    def remove_tmp_dir(self):
        shutil.rmtree(self.path)

    def create_tmp_dir(self):
        return tempfile.mkdtemp()
    
    def __del__(self):
        self.remove_tmp_dir()