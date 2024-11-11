import logging

class LoggerSetup:
    # A simple configuration setter for logging.
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.configure()

    def configure(self, log_path=None):
        console_handler = logging.StreamHandler()
        self.logger.addHandler(console_handler)
        # file_handler = logging.FileHandler("logfile.log", mode="a", encoding="utf-8")
        # self.logger.setLevel(logging.DEBUG)
        self.logger.setLevel(logging.INFO)
        # self.logger.setLevel(logging.WARNING)
        # self.logger.setLevel(logging.ERROR)
        # self.logger.setLevel(logging.CRITICAL)

    def debug(self, text):
        self.logger.debug(text)

    def info(self, text):
        self.logger.info(text)

    def warning(self, text):
        self.logger.warning(text)

    def error(self, text):
        self.logger.error(text)

    def critical(self, text):
        self.logger.critical(text)
