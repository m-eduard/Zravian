from Framework.utils.Logger import get_projectLogger
from contextlib import contextmanager
from Framework.utils.Constants import get_ACCOUNT, get_XPATH
from Framework.utils.SeleniumUtils import SWS


logger = get_projectLogger()
XPATH = get_XPATH()
ACCOUNT = get_ACCOUNT()


@contextmanager
def login(travianURL=ACCOUNT.URL, headless=False, user=ACCOUNT.NAME, password=ACCOUNT.PASS):
    """
    Opens travian and logs in based on given credentials.

    Parameters:
        - travianURL (String): URL to load, taken from account json by default.
        - headless (Boolean): Set to False in order to see browser, False by default.
        - user (String): User used to login, taken from account json by default.
        - password (String): Password used to login, taken from account json by default.
    """
    sws = SWS(headless)
    if sws.get(travianURL):
        if sws.sendKeys(XPATH.LOGIN_USER_INPUT, user):
            if sws.sendKeys(XPATH.LOGIN_PASS_INPUT, password):
                if sws.clickElement(XPATH.LOGIN_SUBMIT_BTN, refresh=True):
                    initString = '<' + 25 * '-' + 'STARTED NEW SESSION' + 25 * '-' + '>'
                    logger.info(initString)
                    yield sws
                else:
                    logger.error('In function login: Failed to click LOGIN_SUBMIT_BTN!')
            else:
                logger.error('In function login: Failed to type text in LOGIN_PASS_INPUT!')
        else:
            logger.error('In function login: Failed to type text in LOGIN_USER_INPUT!')
    else:
        logger.error('In function login: Failed to load {travianURL}!')
    sws.close()
