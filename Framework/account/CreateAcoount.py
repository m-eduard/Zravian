import json
import time
from enum import Enum
from Framework.utils.SeleniumUtils import SWS
from Framework.utils.Logger import get_projectLogger
from Framework.utils.Constants import ACCOUNT_LIBRARY_PATH, Server, Tribe, get_XPATH

logger = get_projectLogger()
XPATH = get_XPATH()
# Notation for undefined field
UNDEFINED = ''

TEMP_EMAIL_URL = 'https://cryptogmail.com/'
DEFAULT_POLLING_TIME = 1
MAX_POLLING_TIME = 20


class Region(Enum):
    PLUS_PLUS = '+|+'
    PLUS_MINUS = '+|-'
    MINUS_PLUS = '-|+'
    MINUS_MINUS = '-|-'


class CreateZravianAccount:
    def __init__(self, headless : bool):
        self.sws = SWS(headless)

    def close(self):
        if self.sws:
            self.sws.close()
        self.sws = None

    # Temporary email page    
    def generate_email(self):
        """
        Opens a new tab and generates a new email.

        Returns:
            - String with new email if operation was successful, None otherwise.
        """
        ret = None
        if self.sws.newTab(TEMP_EMAIL_URL, switchTo=True):
            initialEmail = self.sws.getElementAttribute(XPATH.TE_EMAIL_BOX, 'text')
            if initialEmail:
                if self.sws.clickElement(XPATH.TE_REMOVE_BTN):
                    startTime = time.time()
                    endTime = startTime + MAX_POLLING_TIME
                    while startTime < endTime:
                        email = self.sws.getElementAttribute(XPATH.TE_EMAIL_BOX, 'text')
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
            logger.error('In generate_email: Failed to open new tab')
        return ret

    def activate_zravian_account(self):
        """
        Clicks on the activation link from the activation mail.

        Returns:
            - True if the operation is successful, False otherwise.
        """
        ret = False
        email_opened = False
        if self.sws.switchToTab(TEMP_EMAIL_URL):
            startTime = time.time()
            endTime = startTime + MAX_POLLING_TIME
            while startTime < endTime:
                if self.sws.isVisible(XPATH.TE_ZRAVIAN_MAIL):
                    if self.sws.clickElement(XPATH.TE_ZRAVIAN_MAIL, scrollIntoView=True):
                        email_opened = True
                    else:
                        logger.error('In activate_zravian_account: Failed to click email')
                    break
                time.sleep(DEFAULT_POLLING_TIME)
                startTime = time.time()
            else:
                logger.error('In activate_zravian_account: Failed to receive mail. ' \
                            'This might be due to Temporary email problems')
        else:
            logger.error('In activate_zravian_account: Failed to switch to tab')
        if email_opened:
            ACTIVATE_TEXT = 'activate.php?'
            link = None
            elems = self.sws.getElementAttribute(XPATH.STRING_ON_SCREEN % ACTIVATE_TEXT, 'text', waitFor=True)
            if elems:
                for potential_link in elems[0].split():
                    if ACTIVATE_TEXT in potential_link:
                        link = potential_link
                        break
                else:
                    logger.error('In activate_zravian_account: Failed to extract activation link')
            else:
                logger.error('In activate_zravian_account: Failed to extract activation link')
            if link:
                if self.sws.get(link, checkURL=False):
                    if self.sws.isVisible(XPATH.ZRAVIAN_SUCCESS_STATUS, waitFor=True):
                        ret = True
                        logger.success('Activation successful')
                    else:
                        logger.error('In activate_zravian_account: Success message not found')
                else:
                    logger.error('In activate_zravian_account: Failed to access activation link')
        return ret

    # Zravian registration page
    def generic_credentials_generator(server : Server):
        """
        Creates generic credentials.

        Parameters:
            - server (Server): Server of new account.

        Returns:
            - String
        """
        GENERIC_PHRASE = '0bomb'
        try:
            with open(ACCOUNT_LIBRARY_PATH, 'r') as f:
                jsonData = f.read()
        except IOError:
            logger.error(f'Please ensure that file {ACCOUNT_LIBRARY_PATH} exists and contains the right data')
        try:
            decodedJson = json.loads(jsonData)
        except json.JSONDecodeError:
            logger.error(f'Invalid json format in file {ACCOUNT_LIBRARY_PATH}')
        num = 0
        for acc in decodedJson[f'{server.value}']:
            if acc["username"].startswith(GENERIC_PHRASE):
                try:
                    num = max(num, int(acc["username"][len(GENERIC_PHRASE):]))
                except:
                    pass
        num += 1
        return GENERIC_PHRASE + str(num)

    def fill_registration_data(self, username : str, password : str, emailAddress : str):
        """
        Completes username, password and email fields.

        Parameters:
            - username (str): Username of new account.
            - password (str): Password of new account.
            - emailAddress (str): Email of new account.

        Returns:
            - True if the operation was successful, False otherwise.
        """
        ret = False
        if self.sws.sendKeys(XPATH.REGISTER_USER_INPUT, username) and \
                self.sws.sendKeys(XPATH.REGISTER_PASS1_INPUT, password) and \
                self.sws.sendKeys(XPATH.REGISTER_PASS2_INPUT, password) and \
                self.sws.sendKeys(XPATH.REGISTER_MAIL_INPUT, emailAddress) and \
                self.sws.sendKeys(XPATH.REGISTER_MAIL2_INPUT, emailAddress):
            ret = True
        else:
            logger.error('In fill_registration_data: Error while entering data')
        return ret

    def select_tribe(self, tribe : Tribe):
        """
        Selects tribe during registration.

        Parameters:
            - tribe (Tribe): Tribe of new account.

        Returns:
            - True if operation was successful, False otherwise.
        """
        ret = False
        tribeName = tribe.name[0] + tribe.name[1:-1].lower()
        if self.sws.clickElement(XPATH.STRING_ON_SCREEN % tribeName):
            ret = True
        else:
            logger.error('In select_tribe: Failed to select tribe')
        return ret

    def select_region(self, region : Region):
        """
        Selects tribe during registration.

        Parameters:
            - region (Region): Region of new account.

        Returns:
            - True if operation was successful, False otherwise.
        """
        ret = False
        if self.sws.clickElement(XPATH.STRING_ON_SCREEN % region.value):
            ret = True
        else:
            logger.error('In select_region: Failed to select region')
        return ret

    def agree_and_submit(self):
        """
        Agrees to displayed checkboxes and submits registration form.

        Returns:
            - True if operation is successful, False otherwise.
        """
        ret = False
        if self.sws.clickElement(XPATH.REGISTER_AGREE_1_CHKBOX):  # Always displayed
            if self.sws.isVisible(XPATH.REGISTER_AGREE_2_CHKBOX):  # Not always displayed
                if not self.sws.clickElement(XPATH.REGISTER_AGREE_2_CHKBOX):
                    logger.error('In agree_and_submit: Failed to check second checkbox')
            if self.sws.clickElement(XPATH.REGISTER_SUBMIT_BTN):
                ret = True
            else:
                logger.error('In agree_and_submit: Failed to submit')
        else:
            logger.error('In agree_and_submit: Failed to agree')
        return ret

    def complete_registration_form(self, username : str, password : str, server : Server, emailAddress : str,
                tribe : Tribe, region : Region):
        """
        Opens a new tab and completes the registration form.

        Parameters:
            - username (str): Username of new account.
            - password (str): Password of new account.
            - server (Server): Server of new account.
            - emailAddress (str): Email of new account.
            - tribe (Tribe): Tribe of new account.
            - region (Region): Region of new account.

        Returns:
            - True if the operation was successful, False otherwise.
        """
        ret = False
        REGISTER_SUFFIX = 'register.php'
        if self.sws.newTab(server.value + REGISTER_SUFFIX, switchTo=True):
            if self.fill_registration_data(username, password, emailAddress) and \
                    self.select_tribe(tribe) and self.select_region(region) and self.agree_and_submit():
                if self.registration_error_checker():
                    ret = True
            else:
                logger.error('In complete_registration_form: Failed to complete registration process')
        else:
            logger.error('In complete_registration_form: Failed to open new tab')
        return ret

    def registration_error_checker(self):
        """
        Checks for errors in the registration process.

        Returns:
            - True if the registration was successful, False otherwise.
        """
        status = False
        if self.sws.isVisible(XPATH.ZRAVIAN_ERROR_STATUS):
            errorMsg = self.sws.getElementAttribute(XPATH.ZRAVIAN_ERROR_STATUS_MSG, 'text')
            if errorMsg:
                logger.warning('Registration failed with following message: %s' % errorMsg[0])
            else:
                logger.error('In registration_error_checker: Could not retrieve error message')
        elif self.sws.isVisible(XPATH.ZRAVIAN_SUCCESS_STATUS):
            logger.success('Registration successful')
            status = True
        else:
            logger.error('In registration_error_checker: Failed to find status')
        return status

    # Zravian first login
    def initial_setup(self):
        pass

    # Local account management
    def store_new_account(self, username : str, password : str, server : Server):
        """
        Stores the new account in account library.

        Parameters:
            - username (str): Username of new account.
            - password (str): Password of new account.
            - server (Server): Server of new account.

        Returns:
            - True if the operation was successful, False otherwise.
        """
        ret = False
        NEW_ACCOUNT_JSON = {
            "username": f'{username}',
            "password": f'{password}',
        }
        decodedJson = None
        try:
            with open(ACCOUNT_LIBRARY_PATH, 'r') as f:
                jsonData = f.read()
        except IOError:
            logger.error(f'Please ensure that file {ACCOUNT_LIBRARY_PATH} exists and contains the right data')
        try:
            decodedJson = json.loads(jsonData)
            decodedJson[f'{server.value}'].append(NEW_ACCOUNT_JSON)
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
    def register(self, username : str, password : str, server : Server, tribe : Tribe, region : Region):
        """
        Attempts to complete registration process.

        Parameters:
            - username (str): Username of new account.
            - password (str): Password of new account.
            - server (Server): Server of new account.
            - tribe (Tribe): Tribe of new account.
            - region (Region): Region of new account.

        Returns:
            - True if the operation was successful, False otherwise.
        """
        status = False
        if username == '' or password == '':
            username = password = self.generic_credentials_generator()
        emailAddress = self.generate_email()
        if emailAddress:
            if self.complete_registration_form(username, password, server, emailAddress, tribe, region):
                if self.activate_zravian_account():
                    if self.store_new_account(username, password, server):
                        status = True
                    else:
                        logger.error('In register: Failed to store the new account')
                else:
                    logger.error('In register: Failed to activate the new account')
            else:
                logger.error('In register: Failed to complete the registration form')
        else:
            logger.error('In register: Failed to generate an email address')
        return status

def create_new_account(username : str = UNDEFINED, password : str = UNDEFINED, server=Server.S10k, tribe=Tribe.TEUTONS,
            region=Region.PLUS_PLUS, headless=True):
    """
    Creates and activates a new account.

    Parameters:
        - username (str): username.
        - password (str): password.
        - server (Server): Server of new account.
        - tribe (Tribe): Desired tribe.

    Returns:
        - True if the operation is successful, False otherwise.
    """
    creator = CreateZravianAccount(headless)
    status = creator.register(username, password, server, tribe, region)
    creator.close()
    return status

