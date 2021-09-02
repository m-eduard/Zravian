import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from Framework.utils.SeleniumUtils import clickElement
from Framework.utils.Logger import ProjectLogger
from Framework.utils.Constants import CHROME_DRIVER_PATH, Tribe, get_XPATHS
from Framework.VillageManagement.Utils import XPATH
from enum import Enum

logger = ProjectLogger()
XPATH = get_XPATHS()

BASE_ZRAVIAN_URL = 'https://zravian.com/?nosess'
TEMP_EMAIL_URL = 'https://temp-mail.org/ro/'
REGISTER_BTN = 'Register'


class Server(Enum):
    NONSTOP = 'Nonstop',
    S1 = 'Server 1',
    S5 = 'Server 5',
    S10k = 'Zravian 10k'


class TemporaryEmailWeb:
    def __init__(self, headless) -> None:
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
        self.driver = webdriver.Chrome(chrome_options=options, executable_path=CHROME_DRIVER_PATH)

    def close(self):
        if self.driver:
            self.driver.close()
        self.driver = None
    
    def get_email(self):
        self.driver.get(TEMP_EMAIL_URL)
        # while True:
        #     try:
        #         self.driver.find_element(By.XPATH, XPATH.TE_DISABLED_EMAIL_BOX)
        #     except NoSuchElementException:
        #         break
        #     time.sleep(1)
        elem = self.driver.find_element(By.XPATH, XPATH.TE_COPY_MAIL_BTN)
        print(elem.text)
        elem.click()

x = TemporaryEmailWeb(False)
x.get_email()

# def init_driver(headless):
#     options = webdriver.ChromeOptions()
#     if headless:  # Set headless = False in order to see the browser
#         options.add_argument("--headless")
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-gpu')
#     options.add_argument('--disable-dev-shm-usage')
#     options.add_argument('start-maximized')
#     options.add_argument('disable-infobars')
#     options.add_argument("--disable-extensions")
#     options.add_experimental_option('excludeSwitches', ['enable-logging'])
#     driver = webdriver.Chrome(chrome_options=options, executable_path=CHROME_DRIVER_PATH)
#     return driver


# def create_account(username, password, sv, tribe, headless=True):
#     """
#     Creates a new account on a server.
#     """
#     if isinstance(sv, Server) and isinstance(tribe, Tribe):
#         # Temporary email
#         temp_email_driver = init_driver(headless)
#         # Register
#         driver = init_driver(headless)
#         DEFAULT_REGION = '-|+'
#         driver.get(BASE_ZRAVIAN_URL)
#         if clickElement(driver, XPATH.SERVER_SELECTION % Server[sv]):
#             if clickElement(driver, XPATH.STRING_ON_SCREEN % REGISTER_BTN):

#     else:
#         logger.error('In function create_account: Invalid parameter sv/tribe')


