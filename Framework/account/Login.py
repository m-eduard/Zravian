from contextlib import contextmanager
from Framework.account.AccountLibraryManager import get_account_password
from Framework.missions.missions import accept_missions, skip_missions
from Framework.utility.Constants import Server, get_XPATH
from Framework.utility.Logger import get_projectLogger
from Framework.utility.SeleniumUtils import SWS


# Project constants
logger = get_projectLogger()
XPATH = get_XPATH()


@contextmanager
def login(server : Server, username : str, password=None, headless=False):
    """
    Opens travian and logs in based on given credentials.

    Parameters:
        - server (Server): URL to load, taken from account json by default.
        - username (str): username used to login, taken from account json by default.
        - headless (bool): Set to False in order to see browser, False by default.
        - password (str): Password used to login, taken from account json by default.

    Returns:
        - Yields a SWS object if the operation was successful, None otherwise.
    """
    status = False
    sws = SWS(headless)
    if not password:
        password = get_account_password(server, username)
    if password:
        if sws.get(server.value):
            if sws.sendKeys(XPATH.LOGIN_USER_INPUT, username):
                if sws.sendKeys(XPATH.LOGIN_PASS_INPUT, password):
                    if sws.clickElement(XPATH.LOGIN_SUBMIT_BTN, refresh=True):
                        status = True
                        yield sws
                    else:
                        logger.error('In login: Failed to click LOGIN_SUBMIT_BTN!')
                else:
                    logger.error('In login: Failed to type text in LOGIN_PASS_INPUT!')
            else:
                logger.error('In login: Failed to type text in LOGIN_USER_INPUT!')
        else:
            logger.error('In login: Failed to load {server.value}!')
    else:
        logger.error(f'In login: Failed to identify password for {username} on {server.value}')
    if not status:
        yield None
    sws.close()


def initial_setup(sws : SWS, doTasks=False):
    """
    First login setup.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - doTasks (bool): If set account will do tasks, False by default.

    Returns:
        - True if operation was succesful, False otherwise.
    """
    return (doTasks and accept_missions(sws)) or (not doTasks and skip_missions(sws))
