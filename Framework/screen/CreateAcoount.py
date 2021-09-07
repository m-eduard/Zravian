import json
import time
from selenium import webdriver
from Framework.utils.SeleniumUtils import clickElement, getCurrentUrl, getElementAttribute, isVisible, newTab, sendKeys, get, switchToTab
from Framework.utils.Logger import ProjectLogger
from Framework.utils.Constants import ACCOUNT_LIBRARY_PATH, CHROME_DRIVER_PATH, Tribe, get_XPATHS
from Framework.VillageManagement.Utils import XPATH
from enum import Enum

logger = ProjectLogger()
XPATH = get_XPATHS()

TEMP_EMAIL_URL = 'https://cryptogmail.com/'
DEFAULT_POLLING_TIME = 1
MAX_POLLING_TIME = 20


class Server(Enum):
    NONSTOP = 'https://nonstop.zravian.com/'
    S1 = 'https://s1.zravian.com/'
    S5 = 'https://s5.zravian.com/'
    S10k = 'https://10k.zravian.com/'

class Region(Enum):
    PLUS_PLUS = '+|+'
    PLUS_MINUS = '+|-'
    MINUS_PLUS = '-|+'
    MINUS_MINUS = '-|-'


class CreateZravianAccount:
    def __init__(self, headless):
        # Webdriver
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

    # Temporary email page    
    def generate_email(self):
        """
        Opens a new tab and generates a new email.

        Returns:
            - String with new email if operation was successful, None otherwise.
        """
        ret = None
        if newTab(self.driver, TEMP_EMAIL_URL, switchTo=True):
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
            logger.error('In function generate_email: Failed to open new tab')
        return ret

    def activate_zravian_account(self):
        """
        Clicks on the activation link from the activation mail.

        Returns:
            - True if the operation is successful, False otherwise.
        """
        ret = False
        email_opened = False
        if switchToTab(self.driver, TEMP_EMAIL_URL):
            startTime = time.time()
            endTime = startTime + MAX_POLLING_TIME
            while startTime < endTime:
                if isVisible(self.driver, XPATH.TE_ZRAVIAN_MAIL):
                    if clickElement(self.driver, XPATH.TE_ZRAVIAN_MAIL, scrollIntoView=True):
                        email_opened = True
                    else:
                        logger.error('In function activate_zravian_account: Failed to click email')
                    break
                time.sleep(DEFAULT_POLLING_TIME)
                startTime = time.time()
            else:
                logger.error('In function activate_zravian_account: Failed to receive mail. ' \
                            'This might be due to Temporary email problems')
        else:
            logger.error('In function activate_zravian_account: Failed to switch to tab')
        if email_opened:
            ACTIVATE_TEXT = 'activate.php?'
            link = None
            elems = getElementAttribute(self.driver, XPATH.STRING_ON_SCREEN % ACTIVATE_TEXT, 'text', waitFor=True)
            if elems:
                for potential_link in elems[0].split():
                    if ACTIVATE_TEXT in potential_link:
                        link = potential_link
                        break
                else:
                    logger.error('In function activate_zravian_account: Failed to extract activation link')
            else:
                logger.error('In function activate_zravian_account: Failed to extract activation link')
            if link:
                if get(self.driver, link, checkURL=False):
                    if isVisible(self.driver, XPATH.ZRAVIAN_SUCCESS_STATUS, waitFor=True):
                        ret = True
                        logger.success('Activation successful')
                    else:
                        logger.error('In function activate_zravian_account: Success message not found')
                else:
                    logger.error('In function activate_zravian_account: Failed to access activation link')
        return ret

    # Zravian registration page
    def fill_registration_data(self, username, password, emailAddress):
        """
        Completes username, password and email fields.

        Parameters:
            - username (String): Username of new account.
            - password (String): Password of new account.
            - emailAddress (String): Email of new account.

        Returns:
            - True if the operation was successful, False otherwise.
        """
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
        """
        Selects tribe during registration.

        Parameters:
            - tribe (Tribe): Tribe of new account.

        Returns:
            - True if operation was successful, False otherwise.
        """
        ret = False
        if isinstance(tribe, Tribe):
            tribeName = tribe.name[0] + tribe.name[1:-1].lower()
            if clickElement(self.driver, XPATH.STRING_ON_SCREEN % tribeName):
                ret = True
            else:
                logger.error('In function select_tribe: Failed to select tribe')
        else:
            logger.error('In function select_tribe: Invalid parameter tribe')
        return ret

    def select_region(self, region):
        """
        Selects tribe during registration.

        Parameters:
            - region (Region): Region of new account.

        Returns:
            - True if operation was successful, False otherwise.
        """
        ret = False
        if isinstance(region, Region):
            if clickElement(self.driver, XPATH.STRING_ON_SCREEN % region.value):
                ret = True
            else:
                logger.error('In function select_region: Failed to select region')
        else:
            logger.error('In function select_region: Invalid parameter region')
        return ret

    def agree_and_submit(self):
        """
        Agrees to displayed checkboxes and submits registration form.

        Returns:
            - True if operation is successful, False otherwise.
        """
        ret = False
        if clickElement(self.driver, XPATH.REGISTER_AGREE_1_CHKBOX):  # Always displayed
            if isVisible(self.driver, XPATH.REGISTER_AGREE_2_CHKBOX):  # Not always displayed
                if not clickElement(self.driver, XPATH.REGISTER_AGREE_2_CHKBOX):
                    logger.error('In function agree_and_submit: Failed to check second checkbox')
            if clickElement(self.driver, XPATH.REGISTER_SUBMIT_BTN):
                ret = True
            else:
                logger.error('In function agree_and_submit: Failed to submit')
        else:
            logger.error('In function agree_and_submit: Failed to agree')
        return ret

    def complete_registration_form(self, username, password, server, emailAddress, tribe, region):
        """
        Opens a new tab and completes the registration form.

        Parameters:
            - username (String): Username of new account.
            - password (String): Password of new account.
            - server (Server): Desired tribe.
            - emailAddress (String): Email of new account.
            - tribe (Tribe): Tribe of new account.
            - region (Region): Region of new account.

        Returns:
            - True if the operation was successful, False otherwise.
        """
        ret = False
        REGISTER_SUFFIX = 'register.php'
        if isinstance(server, Server):
            if newTab(self.driver, server.value + REGISTER_SUFFIX, switchTo=True):
                if self.fill_registration_data(username, password, emailAddress) and \
                        self.select_tribe(tribe) and self.select_region(region) and self.agree_and_submit():
                    if self.registration_error_checker():
                        ret = True
                else:
                    logger.error('In function complete_registration_form: Failed to complete registration process')
            else:
                logger.error('In function complete_registration_form: Failed to open new tab')
        else:
            logger.error('In function complete_registration_form: Invalid parameter server')
        return ret

    def registration_error_checker(self):
        """
        Checks for errors in the registration process.

        Returns:
            - True if the registration was successful, False otherwise.
        """
        status = False
        if isVisible(self.driver, XPATH.ZRAVIAN_ERROR_STATUS):
            errorMsg = getElementAttribute(self.driver, XPATH.ZRAVIAN_ERROR_STATUS_MSG, 'text')
            if errorMsg:
                logger.warning('Registration failed with following message: %s' % errorMsg[0])
            else:
                logger.error('In function registration_error_checker: Could not retrieve error message')
        elif isVisible(self.driver, XPATH.ZRAVIAN_SUCCESS_STATUS):
            logger.success('Registration successful')
            status = True
        else:
            logger.error('In function registration_error_checker: Failed to find status')
        return status

    # Local account management
    def store_new_account(self, username, password, server, tribe):
        """
        Stores the new account in account library.

        Parameters:
            - username (String): Username of new account.
            - password (String): Password of new account.
            - server (String): Server of new account.
            - tribe (Tribe): Tribe of new account.

        Returns:
            - True if the operation was successful, False otherwise.
        """
        ret = False
        NEW_ACCOUNT_JSON = {
            "url": f'{server.value}',
            "username": f'{username}',
            "password": f'{password}',
            "tribe": f'{tribe.value.lower()}'
        }
        decodedJson = None
        try:
            with open(ACCOUNT_LIBRARY_PATH, 'r') as f:
                jsonData = f.read()
        except IOError:
            logger.error(f'Please ensure that file {ACCOUNT_LIBRARY_PATH} exists and contains the right data')
        try:
            decodedJson = json.loads(jsonData)
            decodedJson.append(NEW_ACCOUNT_JSON)
        except json.JSONDecodeError:
            logger.error(f'Invalid json format in file {ACCOUNT_LIBRARY_PATH}')
        try:
            with open(ACCOUNT_LIBRARY_PATH, 'w') as f:
                if decodedJson:
                    f.write(json.dumps(decodedJson, indent=4, sort_keys=False))
                    ret = True
        except IOError:
            logger.error(f'Please ensure that file {ACCOUNT_LIBRARY_PATH} exists and contains the right data')
        return ret

    # Main method
    def register(self, username, password, server, tribe, region):
        """
        Attempts to complete registration process.

        Parameters:
            - username (String): Username of new account.
            - password (String): Password of new account.
            - server (Server): Desired tribe.
            - tribe (Tribe): Tribe of new account.
            - region (Region): Region of new account.

        Returns:
            - True if the operation was successful, False otherwise.
        """
        status = False
        emailAddress = self.generate_email()
        if emailAddress:
            if self.complete_registration_form(username, password, server, emailAddress, tribe, region):
                if self.activate_zravian_account():
                    if self.store_new_account(username, password, server, tribe):
                        status = True
                    else:
                        logger.error('In function register: Failed to store the new account')
                else:
                    logger.error('In function register: Failed to activate the new account')
            else:
                logger.error('In function register: Failed to complete the registration form')
        else:
            logger.error('In function register: Failed to generate an email address')
        return status

def create_new_account(username, password, server, tribe, region, headless=True):
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
    creator = CreateZravianAccount(headless)
    return creator.register(username, password, server, tribe, region)


logger.set_debugMode(True)
print(create_new_account('salamxxs1', 'salamerr', Server.S10k, Tribe.TEUTONS, Region.PLUS_PLUS, headless=False))
