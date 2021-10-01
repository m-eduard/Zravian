from datetime import datetime
import Framework.utility.Constants as CONST


# The logger used for the project
class ProjectLogger:
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

    def __init__(self):
        self.debugMode = False
        START_SESSION = '<' + 25 * '-' + 'STARTED NEW SESSION' + 25 * '-' + '>'
        # Print start message
        self.success(START_SESSION)

    def turn_on_debugMode(self):
        """Turns on debug mode."""
        self.debugMode = True

    def success(self, text : str):
        """
        Logs text to log file with a timestamp as success notification.

        Parameters:
            - text (str): Text to log.
        """
        timestamp = datetime.now().strftime(self.TIMESTAMP_FORMAT)
        message = '%s - SUCCESS: %s' % (timestamp, text)
        terminal_message = self.TextColors.SUCCESS + message + self.TextColors.NORMAL
        with open(CONST.LOGS_PATH, 'a+') as f:
            f.write(f'{message}\n')
        if self.debugMode:
            print(terminal_message)

    def info(self, text : str):
        """
        Logs text to log file with a timestamp as informative.

        Parameters:
            - text (str): Text to log.
        """
        timestamp = datetime.now().strftime(self.TIMESTAMP_FORMAT)
        message = '%s - INFO: %s' % (timestamp, text)
        terminal_message = self.TextColors.INFO + message + self.TextColors.NORMAL
        with open(CONST.LOGS_PATH, 'a+') as f:
            f.write(f'{message}\n')
        if self.debugMode:
            print(terminal_message)

    def warning(self, text : str):
        """
        Logs text to log file with a timestamp as warning.

        Parameters:
            - text (str): Text to log.
        """
        timestamp = datetime.now().strftime(self.TIMESTAMP_FORMAT)
        message = '%s - WARNING: %s' % (timestamp, text)
        terminal_message = self.TextColors.WARNING + message + self.TextColors.NORMAL
        with open(CONST.LOGS_PATH, 'a+') as f:
            f.write(f'{message}\n')
        if self.debugMode:
            print(terminal_message)

    def error(self, text : str):
        """
        Logs text to log file with a timestamp as error.

        Parameters:
            - text (str): Text to log.
        """
        timestamp = datetime.now().strftime(self.TIMESTAMP_FORMAT)
        message = '%s - ERROR: %s' % (timestamp, text)
        terminal_message = self.TextColors.ERROR + message + self.TextColors.NORMAL
        with open(CONST.LOGS_PATH, 'a+') as f:
            f.write(f'{message}\n')
        if self.debugMode:
            print(terminal_message)
