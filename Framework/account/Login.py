from Framework.account.AccountLibraryManager import get_account_password
from Framework.screen.Dialog import accept_missions, skip_missions
from Framework.utility.Constants import Server, get_XPATH, get_projectLogger
from Framework.utility.SeleniumWebScraper import SWS


# Project constants
logger = get_projectLogger()
XPATH = get_XPATH()


# Used to mark login specific errors
class LoginError(Exception):
    pass


class Login:
    def __init__(self, server : Server, username : str, password: str = None, headless: bool = False):
        self.server = server
        self.username = username
        self.password = password
        self.headless = headless

    def __enter__(self):
        """Instantiates sws and attempts to login with the given credentials."""
        self.sws = SWS(self.headless)
        if not self.password:
            self.password = get_account_password(self.server, self.username)
        if not self.password:
            err = LoginError(f'In login: Failed to identify password for {self.username} on {self.server.value}')
            logger.error(str(err))
            raise err
        if not self.sws.get(self.server.value):
            err = LoginError(f'In login: Failed to load {self.server.value}!')
            logger.error(str(err))
            raise err
        if not self.sws.sendKeys(XPATH.LOGIN_USER_INPUT, self.username):
            err = LoginError('In login: Failed to insert username!')
            logger.error(str(err))
            raise err
        if not self.sws.sendKeys(XPATH.LOGIN_PASS_INPUT, self.password):
            err = LoginError('In login: Failed to insert password')
            logger.error(str(err))
            raise err
        if not self.sws.clickElement(XPATH.LOGIN_SUBMIT_BTN, refresh=True):
            err = LoginError('In login: Failed to click submit')
            logger.error(str(err))
            raise err
        return self.sws

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Closes sws."""
        if self.sws:
            self.sws.close()
        self.sws = None


def initial_setup(sws : SWS, doTasks):
    """
    First login setup.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - doTasks (bool): If set account will do tasks, False by default.

    Returns:
        - True if operation was succesful, False otherwise.
    """
    return (doTasks and accept_missions(sws)) or (not doTasks and skip_missions(sws))
