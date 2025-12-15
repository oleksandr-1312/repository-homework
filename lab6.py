import os
import logging
import functools

class FileError(Exception):
    pass

class FileNotFound(FileError):
    pass

class FileCorrupted(FileError):
    pass


def logged(exc, mode="console", log_filename="log.txt"):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exc as e:
                logger = logging.getLogger(func.__name__)
                logger.setLevel(logging.ERROR)

                if mode == "console":
                    handler = logging.StreamHandler()
                else:
                    handler = logging.FileHandler(log_filename, mode="a", encoding="utf-8")

                formatter = logging.Formatter("%(asctime)s - %(message)s")
                handler.setFormatter(formatter)
                logger.addHandler(handler)

                logger.error(str(e))

                logger.removeHandler(handler)
                handler.close()
                raise
        return wrapper
    return decorator


class FileHandler:

    @logged(FileNotFound, mode="console")
    def __init__(self, path):
        self.path = path

        if not os.path.exists(path):
            raise FileNotFound(f"File not found: {path}")

        if not path.endswith(".xml"):
            raise FileCorrupted("File must be XML")

    @logged(FileCorrupted, mode="file")
    def read(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return f.read()
        except:
            raise FileCorrupted("Error reading file")

    @logged(FileCorrupted, mode="file")
    def write(self, content):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                f.write(content)
        except:
            raise FileCorrupted("Error writing to file")

    @logged(FileCorrupted, mode="file")
    def append(self, content):
        try:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(content)
        except:
            raise FileCorrupted("Error appending to file")

if __name__ == "__main__":
    try:
        fh = FileHandler("example.xml")
        print(fh.read())
        fh.append("\n<test>123</test>")
        fh.write("<root>updated</root>")
    except FileError as e:
        print("Error:", e)