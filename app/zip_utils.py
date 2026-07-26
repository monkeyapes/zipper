import zipfile
import os
import threading

class ZipExtractor:
    def __init__(self, callback=None):
        self.callback = callback
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def get_contents(self, zip_path):
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                return [(info.filename, info.file_size, info.compress_size) for info in zf.infolist()]
        except Exception as e:
            return str(e)

    def extract(self, zip_path, dest_path):
        self._cancel = False
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                infos = zf.infolist()
                total = len(infos)
                for i, info in enumerate(infos):
                    if self._cancel:
                        if self.callback:
                            self.callback('cancelled', i, total, '')
                        return False
                    zf.extract(info, dest_path)
                    if self.callback:
                        self.callback('progress', i + 1, total, info.filename)
            if self.callback:
                self.callback('done', total, total, '')
            return True
        except Exception as e:
            if self.callback:
                self.callback('error', 0, 0, str(e))
            return False
