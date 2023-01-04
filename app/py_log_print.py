class PyLogPrint:
    def info(self, msg: str):
        print(msg)

    def debug(self, msg: str):
        print(msg)

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        print(msg)


log = PyLogPrint()
