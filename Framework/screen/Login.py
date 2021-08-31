from Framework.utils.Logger import get_projectLogger
from contextlib import contextmanager
from selenium import webdriver
from Framework.utils.Constants import CHROME_DRIVER_PATH, get_ACCOUNT, get_XPATHS
from Framework.utils.SeleniumUtils import get, sendKeys, clickElement


logger = get_projectLogger()
XPATHS = get_XPATHS()
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
    options = webdriver.ChromeOptions()
    if headless:  # Set headless = False in order to see the browser
        options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('start-maximized')
    options.add_argument('disable-infobars')
    options.add_argument("--disable-extensions")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(chrome_options=options, executable_path=CHROME_DRIVER_PATH)
    if get(driver, travianURL):
        if sendKeys(driver, XPATHS.LOGIN_USER_INPUT, user):
            if sendKeys(driver, XPATHS.LOGIN_PASS_INPUT, password):
                if clickElement(driver, XPATHS.LOGIN_SUBMIT_BTN, refresh=True):
                    initString = '<' + 25 * '-' + 'STARTED NEW SESSION' + 25 * '-' + '>'
                    logger.info(initString)
                    yield driver
                else:
                    logger.error('In function login: Failed to click LOGIN_SUBMIT_BTN!')
            else:
                logger.error('In function login: Failed to type text in LOGIN_PASS_INPUT!')
        else:
            logger.error('In function login: Failed to type text in LOGIN_USER_INPUT!')
    else:
        logger.error('In function login: Failed to load {travianURL}!')
    driver.close()
