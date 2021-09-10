from Framework.account.AccountLibraryManager import JSON_PASSWORD_KEY, JSON_USERNAME_KEY, append_account, get_account_library
import json
import time
from enum import Enum, IntEnum
from Framework.utility.SeleniumUtils import SWS
from Framework.utility.Logger import get_projectLogger
from Framework.utility.Constants import Server, Tribe, get_XPATH

logger = get_projectLogger()
XPATH = get_XPATH()
# Notation for undefined field
UNDEFINED = ''
# Error for name in use
ERR_NAME_IN_USE = 'Name in use!'
# URL for temporary email generator site
TEMP_EMAIL_URL = 'https://cryptogmail.com/'
# Polling constants
DEFAULT_POLLING_TIME = 1
MAX_POLLING_TIME = 60
# Generic phrase to include in all accounts
GENERIC_PHRASE = '0bomb'


class Region(Enum):
    PLUS_PLUS = '+|+'
    PLUS_MINUS = '+|-'
    MINUS_PLUS = '-|+'
    MINUS_MINUS = '-|-'


class CreateZravianAccount:
    def __init__(self, headless : bool):
        self.sws = SWS(headless)
        self.register_retrials = 3

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
                            logger.success(f'In generate_email: Generated email {email}')
                            break
                        time.sleep(DEFAULT_POLLING_TIME)
                        startTime = time.time()
                    else:
                        logger.error('In generate_email: Failed to generate new email address')
                else:
                    logger.error('In generate_email: Failed to click remove button')
            else:
                logger.error('In generate_email: Failed to get initial email')
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
                logger.warning('In activate_zravian_account: Failed to receive mail. ' \
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
    def generic_credentials_generator(self, server : Server):
        """
        Creates generic credentials.

        Parameters:
            - server (Server): Server of new account.

        Returns:
            - String
        """
        ret = ''
        decodedJson = get_account_library()
        if decodedJson:
            num = 0
            for acc in decodedJson[server.value]:
                if acc[JSON_USERNAME_KEY].startswith(GENERIC_PHRASE):
                    try:
                        num = max(num, int(acc[JSON_USERNAME_KEY][len(GENERIC_PHRASE):]))
                    except ValueError:
                        pass
            num += 1
            ret = GENERIC_PHRASE + str(num)
        else:
            logger.error('In generic_credentials_generator: Failed to open account library')
        return ret

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
                if self.sws.isVisible(XPATH.ZRAVIAN_SUCCESS_STATUS):
                    logger.success('Registration successful')
                elif self.sws.isVisible(XPATH.ZRAVIAN_ERROR_STATUS):
                    errorMsg = self.sws.getElementAttribute(XPATH.ZRAVIAN_ERROR_STATUS_MSG, 'text')
                    if errorMsg:
                        if errorMsg[0] == ERR_NAME_IN_USE.value:
                            if not self.store_new_account(username, UNDEFINED, server):
                                logger.error('In complete_registration_form: Failed to store account with\
                                    unknown password')
                            else:
                                logger.warning('In complete_registration_form: Added unknown account')
                        else:
                            logger.error(f'In complete_registration_form: Failed with site error {errorMsg[0]}')
                    else:
                        logger.error('In complete_registration_form: Failed to get error message')
                else:
                    logger.error('In complete_registration_form: Unknown registration status')
            else:
                logger.error('In complete_registration_form: Failed to complete registration process')
        else:
            logger.error('In complete_registration_form: Failed to open new tab')
        return ret

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
            JSON_USERNAME_KEY: username,
            JSON_PASSWORD_KEY: password,
        }
        if append_account(NEW_ACCOUNT_JSON, server):
            ret = True
        else:
            logger.error('In store_new_account: Failed to append account to json')
        return ret

    # Register method
    def register(self, username : str, password : str, server : Server, tribe : Tribe, region : Region):
        """
        Attempts to complete registration process.

        Note:
            The process might fail due to errors regarding temporary email.
            The minimal acceptable behavior of this function is to create a `default` account at any given time.

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
        genericAccount = False
        if username == UNDEFINED and password == UNDEFINED:
            genericAccount = True
            username = password = self.generic_credentials_generator(server)
        elif username == UNDEFINED:
            username = self.generic_credentials_generator(server)
        elif password == UNDEFINED:
            password = self.generic_credentials_generator(server)
        emailAddress = self.generate_email()
        if emailAddress:
            if self.complete_registration_form(username, password, server, emailAddress, tribe, region):
                if self.activate_zravian_account():
                    if self.store_new_account(username, password, server):
                        status = True
                    else:
                        logger.error('In register: Failed to store the new account')
                else:
                    if not self.store_new_account(username, UNDEFINED, server):
                        logger.error('In register: Failed to store account with unknown password')
                    logger.warning('In register: Failed to activate the new account')
                    if self.register_retrials > 0 and genericAccount:
                        self.register_retrials -= 1
                        logger.warning('In register: Retrying...')
                        status = self.register(username, password, server, tribe, region)
                    elif self.register_retrials == 0:
                        logger.error('In register: 3 fails when retrying to activate account')
                    else:
                        logger.warning(f'In register: Could not retry register for {username} and {password}')
            else:
                logger.warning('In register: Failed to complete the registration form')
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

