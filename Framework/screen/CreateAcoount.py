import time
from selenium import webdriver
from Framework.utils.SeleniumUtils import clickElement, getCurrentUrl, getElementAttribute, isVisible, newTab, sendKeys, get, switchToTab
from Framework.utils.Logger import ProjectLogger
from Framework.utils.Constants import CHROME_DRIVER_PATH, Tribe, get_XPATHS
from Framework.VillageManagement.Utils import XPATH
from enum import Enum

logger = ProjectLogger()
XPATH = get_XPATHS()

BASE_ZRAVIAN_URL = 'https://zravian.com/'
TEMP_EMAIL_URL = 'https://cryptogmail.com/'
DEFAULT_REGION = '-|+'
ACTIVATION_STRING = 'Your account has been activated and you can now log in'
DEFAULT_POLLING_TIME = 1
MAX_POLLING_TIME = 20


class Server(Enum):
    NONSTOP = 'Nonstop',
    S1 = 'Server 1',
    S5 = 'Server 5',
    S10k = 'Zravian 10k'


class CreateAccount:
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

    def generate_temp_email(self):
        # Driver on TEMP_EMAIL_URL
        ret = None
        if getCurrentUrl(self.driver) == TEMP_EMAIL_URL:
            initialEmail = getElementAttribute(self.driver, XPATH.TE_EMAIL_BOX, 'text')
            if initialEmail:
                if clickElement(self.driver, XPATH.TE_REMOVE_BTN):
                    startTime = time.time()
                    endTime = startTime + MAX_POLLING_TIME
                    while startTime < endTime:
                        email = getElementAttribute(self.driver, XPATH.TE_EMAIL_BOX, 'text')
                        if email and email[0] != initialEmail[0]:
                            ret = str(email[0])
                            break
                        time.sleep(DEFAULT_POLLING_TIME)
                        startTime = time.time()
                    else:
                        logger.error('In get_email: Failed to generate new email address')
                else:
                    logger.error('In get_email: Failed to click remove')
            else:
                logger.error('In get_email: Failed to get initial email')
        else:
            logger.error('Bad page')
        return ret

    def check_email(self):
        ret = False
        if getCurrentUrl(self.driver) == TEMP_EMAIL_URL:
            startTime = time.time()
            endTime = startTime + MAX_POLLING_TIME
            while startTime < endTime:
                if isVisible(self.driver, XPATH.TE_ZRAVIAN_MAIL):
                    if clickElement(self.driver, XPATH.TE_ZRAVIAN_MAIL, scrollIntoView=True):
                        ret = True
                    else:
                        logger.error('In function check_email: Failed to click email')
                    break
                time.sleep(DEFAULT_POLLING_TIME)
                startTime = time.time()
            else:
                logger.error('In function check_email: Failed to find email')
        else:
            logger.error('In function check_email: Bad current page')
        return ret

    def extract_activation_link(self):
        ACTIVATE_TEXT = 'activate.php?'
        link = None
        elems = getElementAttribute(self.driver, XPATH.STRING_ON_SCREEN % ACTIVATE_TEXT, 'text', waitFor=True)
        if elems:
            for potential_link in elems[0].split():
                if ACTIVATE_TEXT in potential_link:
                    link = potential_link
                    break
        else:
            logger.error('In functuon extract_activation_link: Failed to extract activation link')
        return link
        
    def fill_registration_data(self, username, password, emailAddress):
        ret = False
        if sendKeys(self.driver, XPATH.REGISTER_USER_INPUT, username) and \
                sendKeys(self.driver, XPATH.REGISTER_PASS1_INPUT, password) and \
                sendKeys(self.driver, XPATH.REGISTER_PASS2_INPUT, password) and \
                sendKeys(self.driver, XPATH.REGISTER_MAIL_INPUT, emailAddress) and \
                sendKeys(self.driver, XPATH.REGISTER_MAIL2_INPUT, emailAddress):
            ret = True
        else:
            logger.error('In fill_registration_data: Error while entering data')
        return ret

    def select_tribe(self, tribe):
        ret = False
        tribeName = tribe.name[0] + tribe.name[1:-1].lower()
        if clickElement(self.driver, XPATH.STRING_ON_SCREEN % tribeName):
            ret = True
        else:
            logger.error('In function select_tribe: Failed to select tribe')
        return ret

    def select_region(self, region=DEFAULT_REGION):
        ret = False
        if clickElement(self.driver, XPATH.STRING_ON_SCREEN % DEFAULT_REGION):
            ret = True
        else:
            logger.error('In function select_tribe: Failed to select tribe')
        return ret

    def agree_and_submit(self):
        ret = False
        if clickElement(self.driver, XPATH.REGISTER_AGREE_1_CHKBOX):
            if isVisible(self.driver, XPATH.REGISTER_AGREE_2_CHKBOX):
                if not clickElement(self.driver, XPATH.REGISTER_AGREE_2_CHKBOX):
                    logger.error('In function agree_and_submit: Failed to agree second checkbox')
            if clickElement(self.driver, XPATH.REGISTER_SUBMIT_BTN):
                ret = True
            else:
                logger.error('In function agree_and_submit: Failed to submit')
        else:
            logger.error('In function agree_and_submit: Failed to agree')
        return ret

    def fill_registration_page(self, username, password, emailAddress, tribe):
        ret = False
        if self.fill_registration_data(username, password, emailAddress) and \
                self.select_tribe(tribe) and self.select_region() and self.agree_and_submit():
            ret = True
        else:
            logger.error('In function fill_registration_page: Failed to enter data')
        return ret

    def store_new_account(self):
        pass

    def register(self, username, password, sv, tribe):
        status = False
        # Create tabs
        if get(self.driver, TEMP_EMAIL_URL) and newTab(self.driver, BASE_ZRAVIAN_URL):
            # Generate email
            registrationDone = False
            activationDone = False
            if switchToTab(self.driver, TEMP_EMAIL_URL):
                emailAddress = self.generate_temp_email()
                # Switch to register tab
                if emailAddress:
                    if switchToTab(self.driver, BASE_ZRAVIAN_URL):
                        if isinstance(sv, Server) and isinstance(tribe, Tribe):
                            self.driver.get(BASE_ZRAVIAN_URL)
                            if clickElement(self.driver, XPATH.SERVER_SELECTION % sv.value):
                                if clickElement(self.driver, XPATH.REGISTER_BTN):
                                    if self.fill_registration_page(username, password, emailAddress, tribe):
                                        if isVisible(self.driver, XPATH.ZRAVIAN_SUCCESS_STATUS):
                                            registrationDone = True
                                        else:
                                            logger.error('In function register: Status failed')
                                    else:
                                        logger.error('In function register: Failed to enter data')
                                else:
                                    logger.error('In function register: Failed to press register')
                            else:
                                logger.error('In function register: Failed to select server')    
                        else:
                            logger.error('In function register: Invalid parameter sv/tribe')
                    else:
                        logger.error('In function register: Failed to switch tab')
                else:
                    logger.error('In function register: Failed to generate email address')
            if registrationDone:
                # Switch to email tab
                if switchToTab(self.driver, TEMP_EMAIL_URL):
                    if self.check_email():
                        link = self.extract_activation_link()
                        if link:
                            if get(self.driver, link):
                                activationDone = True
                            else:
                                logger.error('In function register: Failed to access activation link')
                        else:
                            logger.error('In function register: Failed to get the activation link')
                    else:
                        logger.error('In function register: Failed to receive the activation link')
                else:
                    logger.error('In function register: Failed to switch tab')
        else:
            logger.error('In function register: Failed to open tabs')
        # Ensure activation was successful
        if activationDone and isVisible(self.driver, XPATH.ZRAVIAN_SUCCESS_STATUS):
            status = True
        self.close()
        return status


def create_new_account(username, password, server, tribe, headless=True):
    """
    Creates and activates a new account.

    Parameters:
        - username (String): username.
        - password (String): password.
        - server (Server): Desired tribe.
        - tribe (Tribe): Desired tribe.

    Returns:
        - True if the operation is successful, False otherwise.
    """
    creator = CreateAccount(headless)
    return creator.register(username, password, server, tribe)
