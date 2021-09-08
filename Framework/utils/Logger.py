from datetime import datetime
from Framework.utils.Constants import LOGS_PATH


# Format for log timestamp
TIMESTAMP_FORMAT = "%d/%m/%y %H:%M:%S"


class TextColors:
    SUCCESS = '\033[92m'
    INFO = '\033[96m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    NORMAL = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class ProjectLogger:
    def __init__(self):
        self.debugMode = False

    def set_debugMode(self, status):
        """
        Sets debug mode to True or False.

        Parameters:
            - status (Boolean): Value to set debugMode to.
        """
        if isinstance(status, bool):
            self.debugMode = status

    def success(self, text : str):
        """
        Logs text to log file with a timestamp as success notification.

        Parameters:
            - text (str): Text to log.
        """
        timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
        message = '%s - SUCCESS: %s' % (timestamp, text)
        terminal_message = TextColors.SUCCESS + message + TextColors.NORMAL
        with open(LOGS_PATH, 'a+') as f:
            f.write(f'{message}\n')
        if self.debugMode:
            print(terminal_message)

    def info(self, text : str):
        """
        Logs text to log file with a timestamp as informative.

        Parameters:
            - text (str): Text to log.
        """
        timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
        message = '%s - INFO: %s' % (timestamp, text)
        terminal_message = TextColors.INFO + message + TextColors.NORMAL
        with open(LOGS_PATH, 'a+') as f:
            f.write(f'{message}\n')
        if self.debugMode:
            print(terminal_message)

    def warning(self, text : str):
        """
        Logs text to log file with a timestamp as warning.

        Parameters:
            - text (str): Text to log.
        """
        timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
        message = '%s - WARNING: %s' % (timestamp, text)
        terminal_message = TextColors.WARNING + message + TextColors.NORMAL
        with open(LOGS_PATH, 'a+') as f:
            f.write(f'{message}\n')
        if self.debugMode:
            print(terminal_message)

    def error(self, text : str):
        """
        Logs text to log file with a timestamp as error.

        Parameters:
            - text (str): Text to log.
        """
        timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
        message = '%s - ERROR: %s' % (timestamp, text)
        terminal_message = TextColors.ERROR + message + TextColors.NORMAL
        with open(LOGS_PATH, 'a+') as f:
            f.write(f'{message}\n')
        if self.debugMode:
            print(terminal_message)


logger = None

def get_projectLogger():
    global logger
    if not logger:
        logger = ProjectLogger()
    return logger
