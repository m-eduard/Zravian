from enum import Enum
import re
import time
from Framework.account.AccountLibraryManager import append_account, get_generic_accounts, get_last_account_username, \
    get_last_account_password
from Framework.account.Login import initial_setup, login
from Framework.utility.Constants import Server, Tribe, get_XPATH, get_projectLogger 
from Framework.utility.SeleniumWebScraper import SWS, Attr


# Project constants
logger = get_projectLogger()
XPATH = get_XPATH(
# Generic phrase to include in all accounts (At least 5 characters long)
GENERIC_PHRASE = '0bomb'
# URL for temporary email generator site
TEMP_EMAIL_URL = 'https://mailpoof.com/'
# Polling constants
DEFAULT_POLLING_TIME = 1
MAX_POLLING_TIME = 60
# Unknown element
UNKNOWN = ''
# Error for name in use
ERR_NAME_IN_USE = 'Name in use!'


class _Region(Enum):
    PLUS_PLUS = '+|+'
    PLUS_MINUS = '+|-'
    MINUS_PLUS = '-|+'
    MINUS_MINUS = '-|-'


class _AccountCreator:
    def __init__(self, headless : bool):
        self.sws = SWS(headless)

    def close(self):
        if self.sws:
            self.sws.close()
        self.sws = None

    # Required in order to use 'with' keyword
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback): 
        self.close()

    # Temporary email page
    def generate_email(self):
        """
        Opens a new tab and generates a new email.

        Returns:
            - String with new email if operation was successful, None otherwise.
        """
        ret = None
        if self.sws.newTab(TEMP_EMAIL_URL, switchTo=True):
            # Generate a new email
            if self.sws.clickElement(XPATH.TE_RANDOM_BTN, refresh=True, scrollIntoView=True, javaScriptClick=True):
                email = self.sws.getElementAttribute(XPATH.TE_EMAIL_ADDRESS, Attr.VALUE)
                if email:
                    ret = str(email)
                    logger.success(f'In generate_email: Generated email {email}')
                else:
                    logger.error('In generate_email: Failed to get the email address')
            else:
                logger.error('In generate_email: Failed to press `Random` button')
        else:
            logger.error('In generate_email: Failed to open new tab')
        return ret

    def activate_zravian_account(self):
        """
        Switches to email tab and clicks on the activation link from the activation mail.

        Returns:
            - True if the operation is successful, False otherwise.
        """
        ret = False
        email_id = None
        if self.sws.switchToTab(TEMP_EMAIL_URL):
            # Wait for zravian activation mail
            startTime = time.time()
            endTime = startTime + MAX_POLLING_TIME
            while startTime < endTime:
                if self.sws.isVisible(XPATH.TE_ZRAVIAN_MAIL):
                    # Extract the email id in order to see its content
                    email_id = self.sws.getElementAttribute(XPATH.TE_ZRAVIAN_MAIL, Attr.ID)
                    if email_id:
                        # Open email
                        if not self.sws.clickElement(XPATH.TE_ZRAVIAN_MAIL, scrollIntoView=True, javaScriptClick=True):
                            email_id = None
                            logger.error('In activate_zravian_account: Failed to click email')
                    else:
                            logger.error('In activate_zravian_account: Failed to extract email id')  
                    break
                time.sleep(DEFAULT_POLLING_TIME)
                startTime = time.time()
                # Refresh mail section to check for new emails
                if not self.sws.clickElement(XPATH.TE_REFRESH_BTN):
                    logger.error('In activate_zravian_account: Failed to refresh')
            else:
                logger.warning('In activate_zravian_account: Failed to receive mail.')
        else:
            logger.error('In activate_zravian_account: Failed to switch to tab')
        # If email id was retrieved and email is open
        if email_id:
            ACTIVATE_TEXT = r'activate\.php\?'
            link = None
            # Extract text from the activation email
            text = self.sws.getElementAttribute(XPATH.TE_EMAIL_TEXT % email_id, Attr.TEXT, waitFor=True)
            if text:
                try:
                    # Seacrh the activation link
                    link = re.search(f'[^ \n]*{ACTIVATE_TEXT}[^ \n]*', text).group()
                except AttributeError:
                    logger.error('In activate_zravian_account: Failed to extract activation link')
            else:
                logger.error('In activate_zravian_account: Failed to extract activation link')
            if link:
                # Click the link and check for success status
                if self.sws.get(link, checkURL=False):
                    if self.sws.isVisible(XPATH.ZRAVIAN_SUCCESS_STATUS, waitFor=True):
                        ret = True
                        logger.success('In activate_zravian_account: Activation successful')
                    else:
                        logger.error('In activate_zravian_account: Success message not found')
                else:
                    logger.error('In activate_zravian_account: Failed to access activation link')
        return ret

    # Zravian registration page
    @staticmethod
    def generic_credentials_generator(server : Server):
        """
        Creates generic credentials.

        Parameters:
            - server (Server): Server of new account.

        Returns:
            - String if operation is successful, None otherwise.
        """
        ret = None
        # Generic phrase min length
        GENERIC_PHRASE_MIN_LEN = 5
        if len(GENERIC_PHRASE) >= GENERIC_PHRASE_MIN_LEN:
            # Find the last generic name and generate the next
            accountList = get_generic_accounts(server, GENERIC_PHRASE)
            if accountList is not None:
                num = 0
                for acc in accountList:
                    accountRegex = re.search(f'{GENERIC_PHRASE}([0-9]+)', acc)
                    try:
                        num = max(num, int(accountRegex.group(1)))
                    except (AttributeError, ValueError):
                        # Found an account not respecting the pattern so ignore it
                        pass
                num += 1
                ret = GENERIC_PHRASE + str(num)
            else:
                logger.error('In generic_credentials_generator: Failed to get account list')
        else:
            logger.error(f'In generic_credentials_generator: Generic phrase {GENERIC_PHRASE} is too short')
        return ret

    @staticmethod
    def validate_input(username : str, password : str, emailAddress : str, tribe : Tribe, region : Tribe):
        """
        Validates the input.

        Parameters:
            - username (str): Username of new account.
            - password (str): Password of new account.
            - server (Server): Server of new account.
            - emailAddress (str): Email of new account.
            - tribe (Tribe): Tribe of new account.
            - region (_Region): Region of new account.

        Returns:
            - True if the input is valid, False otherwise.
        """
        ret = False
        # Password is required to be at least 6 characters long
        MIN_PASSWORD_LEN = 6
        # Check account data to be valid
        if username:
            if password and len(password) >= MIN_PASSWORD_LEN:
                if emailAddress and re.search(r'.+@.+\..+', emailAddress):
                    if tribe:
                        if region:
                            ret = True
                        else:
                            logger.error('In validate_input: Region is missing')
                    else:
                        logger.error('In validate_input: Tribe is missing')
                else:
                    logger.error('In validate_input: Email address bad format')
            else:
                logger.error('In validate_input: Password is too short')
        else:
            logger.error('In validate_input: Username is missing')
        return ret

    def complete_registration_form(self, username : str, password : str, server : Server, emailAddress : str,
                tribe : Tribe, region : _Region):
        """
        Completes the whole registration procedure:
            - Checks validity of input;
            - Opens a new tab with the registration page, fills data (username, password, email, tribe) and 
            the form;
            - Checks status and handles `name in use` error by storing the username with an unknown password.

        Parameters:
            - username (str): Username of new account.
            - password (str): Password of new account.
            - emailAddress (str): Email of new account.
            - tribe (Tribe): Tribe of new account.
            - region (_Region): Region of new account.

        Returns:
            - True if the operation was successful, False otherwise.
        """
        ret = False
        personalContentDone = False
        tribeRegionDone = False
        agreeSubmitDone = False
        # Register section on zravian server
        REGISTER_SUFFIX = 'register.php'
        # Enter personal content
        if _AccountCreator.validate_input(username, password, emailAddress, tribe, region):
            if self.sws.newTab(server.value + REGISTER_SUFFIX, switchTo=True):
                if self.sws.sendKeys(XPATH.NEW_ACC_USER_INPUT, username) and \
                        self.sws.sendKeys(XPATH.NEW_ACC_PASS1_INPUT, password) and \
                        self.sws.sendKeys(XPATH.NEW_ACC_PASS2_INPUT, password) and \
                        self.sws.sendKeys(XPATH.NEW_ACC_MAIL_INPUT, emailAddress) and \
                        self.sws.sendKeys(XPATH.NEW_ACC_MAIL2_INPUT, emailAddress):
                    personalContentDone = True
                else:
                    logger.error('In complete_registration_form: Error while entering data')
            else:
                logger.error('In complete_registration_form: Failed to open new tab')
        # Enter tribe and region
        if personalContentDone:
            if self.sws.clickElement(XPATH.STRING_ON_SCREEN % tribe.name.title()[:-1]):
                if self.sws.clickElement(XPATH.STRING_ON_SCREEN % region.value):
                    tribeRegionDone = True
                else:
                    logger.error('In complete_registration_form: Failed to select region')
            else:
                logger.error('In complete_registration_form: Failed to select tribe')
        # Agree and submit
        if tribeRegionDone:
            if self.sws.clickElement(XPATH.NEW_ACC_AGREE_1_CHKBOX):
                secondCheckboxAgree = True
                # Second checkbox might be missing
                if self.sws.isVisible(XPATH.NEW_ACC_AGREE_2_CHKBOX):
                    if not self.sws.clickElement(XPATH.NEW_ACC_AGREE_2_CHKBOX):
                        secondCheckboxAgree = False
                        logger.error('In complete_registration_form: Failed to check second checkbox')
                if secondCheckboxAgree and self.sws.clickElement(XPATH.NEW_ACC_SUBMIT_BTN):
                    agreeSubmitDone = True
                else:
                    logger.error('In complete_registration_form: Failed to submit')
            else:
                logger.error('In complete_registration_form: Failed to agree')
        # Verify status
        if agreeSubmitDone:
            # Check for success status
            if self.sws.isVisible(XPATH.ZRAVIAN_SUCCESS_STATUS):
                ret = True
                logger.success('Registration successful')
            elif self.sws.isVisible(XPATH.ZRAVIAN_ERROR_STATUS):
                errorMsg = self.sws.getElementAttribute(XPATH.ZRAVIAN_ERROR_STATUS_MSG, Attr.TEXT)
                if errorMsg:
                    # If the name is in use, add the account to `account_library.json` and marked password
                    # as unknown
                    logger.error(f'In complete_registration_form: Failed with site error {errorMsg}')
                    if errorMsg == ERR_NAME_IN_USE:
                        if not self.store_new_account(server, username, UNKNOWN):
                            logger.error('In complete_registration_form: Failed to store account with \
                                unknown password')
                        else:
                            logger.warning('In complete_registration_form: Added unknown account')
                else:
                    logger.error('In complete_registration_form: Failed to get error message')
            else:
                logger.error('In complete_registration_form: Unknown registration status')
        return ret

    # Local account management
    def store_new_account(self, server : Server, username : str, password : str):
        """
        Stores the new account in account library.

        Parameters:
            - server (Server): Server of new account.
            - username (str): Username of new account.
            - password (str): Password of new account.

        Returns:
            - True if the operation was successful, False otherwise.
        """
        ret = False
        if append_account(server, username, password):
            ret = True
        else:
            logger.error('In store_new_account: Failed to append account to json')
        return ret

    # Main method
    def register(self, username : str, password : str, server : Server, tribe : Tribe, region : _Region):
        """
        Attempts to complete registration process.

        Parameters:
            - username (str): Username of new account.
            - password (str): Password of new account.
            - server (Server): Server of new account.
            - tribe (Tribe): Tribe of new account.
            - region (_Region): Region of new account.

        Returns:
            - True if the operation was successful, False otherwise.
        """
        ret = False
        if not username and not password:
            username = password = _AccountCreator.generic_credentials_generator(server)
        elif not username:
            username = _AccountCreator.generic_credentials_generator(server)
        elif not password:
            password = _AccountCreator.generic_credentials_generator(server)
        if username and password:
            emailAddress = self.generate_email()
            if emailAddress:
                if self.complete_registration_form(username, password, server, emailAddress, tribe, region):
                    if self.activate_zravian_account():
                        if self.store_new_account(server, username, password):
                            logger.success(f'In register: Created and saved account [{username}, {password}] on '\
                                f'server {server.value}')
                            ret = True
                        else:
                            logger.error('In register: Failed to store the new account')
                    else:
                        if not self.store_new_account(server, username, UNKNOWN):
                            logger.error('In register: Failed to store account with unknown password')
                        logger.warning('In register: Failed to activate the new account')
                else:
                    logger.warning('In register: Failed to complete the registration form')
            else:
                logger.error('In register: Failed to generate an email address')
        else:
            logger.error('In register: Failed to generate proper username and password')
        return ret


def create_new_account(username : str = None, password : str = None, server=Server.S10k, tribe=Tribe.TEUTONS,
            region=_Region.PLUS_PLUS, doTasks=True, headless=True):
    """
    Creates and activates a new account.

    Parameters:
        - username (str): username, None by default.
        - password (str): password, None by default.
        - server (Server): Server of new account, 10K by default.
        - tribe (Tribe): Desired tribe, Teutons by default.
        - region (_Region): Desired region, +|+ by default.
        - doTasks (bool): If True will accept tasks, False by default.

    Returns:
        - True if the operation is successful, False otherwise.
    """
    ret = False
    # Register account
    registerStatus = False
    with _AccountCreator(headless) as newAcc:
        registerStatus = newAcc.register(username, password, server, tribe, region)
    if registerStatus:
        username, password = get_last_account_username(server), get_last_account_password(server)
        if username and password:
            # Login on the new account
            with login(server, username, password, headless=True, ) as sws:
                # Perform initial configuration
                if sws:
                    if initial_setup(sws, doTasks):
                        ret = True
                    else:
                        logger.error('In create_new_account: Failed to do the initial setup')
        else:
            logger.error('In create_new_account: Failed to retrieve credentials of created account')
    else:
        logger.error('In create_new_account: Failed to register')
    return ret
