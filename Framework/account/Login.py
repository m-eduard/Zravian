import time
from Framework.account.AccountLibraryManager import JSON_PASSWORD_KEY, get_account
from contextlib import contextmanager
from Framework.utility.Logger import get_projectLogger
from Framework.utility.Constants import Server, get_XPATH
from Framework.utility.SeleniumUtils import SWS


logger = get_projectLogger()
XPATH = get_XPATH()
# Notation for undefined field
UNDEFINED = ''
# Continue button
CONTINUE_BTN_TEXT = 'Continue'
# Accept tasks text
ACCEPT_TASKS_TEXT = 'To the first task!'
# Refuse tasks text
REFUSE_TASKS_TEXT = 'Skip tasks'


def get_account_password(username : str, server : Server):
    """
    Retrieves password for given account.

    Parameters:
        - username (str): username used to login, taken from account json by default.
        - server (Server): URL to load, taken from account json by default.
    
    Returns:
        - String if account was found, None otherwise.
    """
    ret = None
    account = get_account(username, server)
    if account:
        ret = account[JSON_PASSWORD_KEY]
    else:
        logger.error('In get_account_password: Failed to get `account_library.json`')
    return ret


@contextmanager
def login(server : Server, username : str, headless=False, password=UNDEFINED):
    """
    Opens travian and logs in based on given credentials.

    Parameters:
        - server (Server): URL to load, taken from account json by default.
        - username (str): username used to login, taken from account json by default.
        - headless (bool): Set to False in order to see browser, False by default.
        - password (str): Password used to login, taken from account json by default.
    """
    sws = SWS(headless)
    if password == UNDEFINED:
        password = get_account_password(username, server)
    if sws.get(server.value):
        if sws.sendKeys(XPATH.LOGIN_USER_INPUT, username):
            if sws.sendKeys(XPATH.LOGIN_PASS_INPUT, password):
                if sws.clickElement(XPATH.LOGIN_SUBMIT_BTN, refresh=True):
                    initString = '<' + 25 * '-' + 'STARTED NEW SESSION' + 25 * '-' + '>'
                    logger.success(initString)
                    yield sws
                else:
                    logger.error('In login: Failed to click LOGIN_SUBMIT_BTN!')
            else:
                logger.error('In login: Failed to type text in LOGIN_PASS_INPUT!')
        else:
            logger.error('In login: Failed to type text in LOGIN_USER_INPUT!')
    else:
        logger.error('In login: Failed to load {server.value}!')
    sws.close()


def initial_setup(sws : SWS, doTasks=False):
        """
        First login setup.

        Parameters:
            - sws (SWS): Selenium Web Scraper
            - doTasks (bool): If set account will do tasks, False by default.

        Returns:
            - True if operation was succesful, False otherwise.
        """
        ret = False
        if sws.isVisible(XPATH.STRING_ON_SCREEN % 'Welcome to Zravian!'):
            print('PLM')
        if sws.clickElement(XPATH.STRING_ON_SCREEN % CONTINUE_BTN_TEXT, refresh=True, waitFor=True):
            if doTasks:
                if sws.clickElement(XPATH.STRING_ON_SCREEN % ACCEPT_TASKS_TEXT, waitFor=True, javaScriptClick=True):
                    logger.success('In initial_setup: Accepted tasks')
                    ret = True
                else:
                    logger.error('In initial_setup: Failed to accept tasks')
            else:
                if sws.clickElement(XPATH.STRING_ON_SCREEN % REFUSE_TASKS_TEXT, waitFor=True, javaScriptClick=True):
                    if sws.clickElement(XPATH.STRING_ON_SCREEN % REFUSE_TASKS_TEXT, waitFor=True, \
                            javaScriptClick=True):
                        if sws.clickElement(XPATH.STRING_ON_SCREEN % REFUSE_TASKS_TEXT, waitFor=True, \
                                javaScriptClick=True):
                            logger.success('In initial_setup: Refused tasks')
                            ret = True
                        else:
                            logger.error('In initial_setup: Failed to press "Skip tasks" third time')
                    else:
                        logger.error('In initial_setup: Failed to press "Skip tasks" second time')
                else:
                    logger.error('In initial_setup: Failed to press "Skip tasks" first time')
        else:
            logger.error('In initial_setup: Failed to click continue button')
        return ret
