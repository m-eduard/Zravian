import json
from contextlib import contextmanager
from Framework.utility.Logger import get_projectLogger
from Framework.utility.Constants import ACCOUNT_LIBRARY_PATH, Server, get_XPATH
from Framework.utility.SeleniumUtils import SWS


logger = get_projectLogger()
XPATH = get_XPATH()
# Notation for undefined field
UNDEFINED = ''


def get_account_password(server : Server, username : str):
    """
    Retrieves password for given account.

    Parameters:
        - server (Server): URL to load, taken from account json by default.
        - username (str): username used to login, taken from account json by default.
    
    Returns:
        - String if account was found, None otherwise.
    """
    ret = None
    try:
        with open(ACCOUNT_LIBRARY_PATH, 'r') as f:
            jsonData = f.read()
    except IOError:
        logger.error(f'Please ensure that file {ACCOUNT_LIBRARY_PATH} exists and contains the right data')
    try:
        decodedJson = json.loads(jsonData)
    except json.JSONDecodeError:
        logger.error(f'Invalid json format in file {ACCOUNT_LIBRARY_PATH}')
    try:
        ret = decodedJson[f'{server.value}'][f'{username}']["password"]
    except:
        logger.error(f'Failed to find password for {server.value}: {username}')
    return ret


@contextmanager
def login(server : Server, username : str, headless=False, password=UNDEFINED):
    """
    Opens travian and logs in based on given credentials.

    Parameters:
        - server (Server): URL to load, taken from account json by default.
        - username (str): username used to login, taken from account json by default.
        - headless (Boolean): Set to False in order to see browser, False by default.
        - password (str): Password used to login, taken from account json by default.
    """
    sws = SWS(headless)
    if password == UNDEFINED:
        password = get_account_password(server, username)
    if sws.get(server.value):
        if sws.sendKeys(XPATH.LOGIN_USER_INPUT, username):
            if sws.sendKeys(XPATH.LOGIN_PASS_INPUT, password):
                if sws.clickElement(XPATH.LOGIN_SUBMIT_BTN, refresh=True):
                    initString = '<' + 25 * '-' + 'STARTED NEW SESSION' + 25 * '-' + '>'
                    logger.info(initString)
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
