from enum import Enum
import re
from Framework.utility.Constants import ResourceType, Server, get_XPATH, get_projectLogger
from Framework.utility.SeleniumWebScraper import SWS, Attr


# Project constants
logger = get_projectLogger()
XPATH = get_XPATH()


# All screens
class Screen(Enum):
    OVERVIEW = 'village1.php'
    VILLAGE = 'village2.php'
    MAP = 'map.php'
    STATISTICS = 'statistics.php'
    PROFILE = 'profile.php'
    MESSAGES = 'msg.php'
    REPORTS = 'report.php'


# Values that might be retrieved from instructions
class InstructionsSearchItem(Enum):
    COSTS = XPATH.INSTRUCTIONS_COSTS


# Utils
def __get_current_screen(sws: SWS):
    """
    Tells which screen is active.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - Current screen if operation was successful, None otherwise.
    """
    ret = None
    URL = sws.getCurrentUrl()
    for screen in Screen:
        if screen.value in URL:
            ret = screen
            break
    else:
        logger.error(f'In __get_current_screen: Unknown screen for {URL}')
    return ret


def __move_to_screen(sws: SWS, screen: Screen, forced: bool):
    """
    Ensures that the current screen is the desired screen.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - screen (Screen): Desired screen.
        - forced (bool): If True and on the desired screen will refresh page.

    Returns:
        - True if the operation was successful, False otherwise.
    """
    ret = False
    if screen != __get_current_screen(sws) or forced:
        BASE_URL = sws.getCurrentUrl().rsplit("/", 1)[0] + '/'
        if sws.get(BASE_URL + screen.value):
            ret = True
        else:
            logger.error(f'In __move_to_screen: Failed to move to {screen.name}')
    else:
        ret = True
    return ret


def __search_in_instructions(sws: SWS, locators: list, item: InstructionsSearchItem):
    """
    Searches information in instructions menu.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - locators ([str]): List with names to incrementally search for instructions page.
        - item (InstructionsSearchItem): Property to extract from last name.

    Returns:
        - String with requested value, None if error occured.
    """
    ret = None
    # Instructions menu text
    INSTRUCTIONS_MENU = 'Instructions'
    # Instructions iframe name
    INSTRUCTIONS_IFRAME = 'Frame'
    # Open instructions menu
    if sws.clickElement(XPATH.STRING_ON_SCREEN % INSTRUCTIONS_MENU):
        sws.enter_iframe(INSTRUCTIONS_IFRAME)
        for locator in locators:
            if sws.isVisible(XPATH.STRING_ON_SCREEN % locator):
                if not sws.clickElement(XPATH.STRING_ON_SCREEN % locator):
                    logger.error(f'In __search_in_instructions: SWS.clickElement() failed')
                    break
            else:
                logger.error(f'In __search_in_instructions: Failed to find {locator}')
                break
        else:
            ret = sws.getElementAttribute(item.value, Attr.TEXT)
        sws.exit_iframe()
        if not sws.clickElement(sws.MISSION_CLOSE_BTN):
            ret = None
            logger.error('In __search_in_instructions: SWS.clickElement() failed')
    else:
        logger.error('In __search_in_instructions: SWS.clickElement() failed')
    return ret


# User UI
def press_continue_btn(sws: SWS):
    """
    Presses the continue button after first ever login.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - True if the operation was successful, False otherwise.
    """
    ret = False
    # Continue button text
    CONTINUE_BTN_TEXT = 'Continue'
    if sws.clickElement(XPATH.STRING_ON_SCREEN % CONTINUE_BTN_TEXT, refresh=True):
        ret = True
    else:
        logger.error('In press_continue_btn: SWS.clickElement() failed')
    return ret


def get_server(sws: SWS):
    """
    Gets the current server.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - Current server if operation is successful, None otherwise.
    """
    ret = None
    serverURL = None
    try:
        serverURL = re.match(r'(.*)\/(.*)', sws.getCurrentUrl()).group(1) + '/'
    except AttributeError as err:
        logger.error(f'In get_server: Regex failed to extract server: {err}')
    if serverURL:
        for server in Server:
            if server.value == serverURL:
                ret = server
                break
        else:
            logger.error(f'In get_server: Unknown server {serverURL}')
    return ret


def instructions_get_costs(sws: SWS, locators: list):
    """
    Searches costs information for building/troop.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - locators ([str]): List with names to incrementally search for instructions page.

    Returns:
        - List containing: Lumber, Clay, Iron, Crop and Upkeep or None if error encountered.
    """
    ret = None
    costsText = __search_in_instructions(sws, locators, InstructionsSearchItem.COSTS)
    if costsText:
        # Take second row and split at each '|', leaving out the last one
        try:
            ret = costsText.split('\n')[1].split('|')[:-1]
        except IndexError:
            logger.error(f'In instructions_get_costs: Costs do not respect pattern {costsText}')
    else:
        logger.error('In instructions_get_costs: __search_in_instructions() failed')
    return ret


# Village dependent
def get_storage(sws: SWS):
    """
    Gets for storage for each resource for current village.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
    
    Returns:
        - Dictionary mapping each resource field to tuple.
    """
    storage = {}
    # Extract lumber storage
    lumber = sws.getElementAttribute(XPATH.PRODUCTION_LUMBER, Attr.TEXT)
    if lumber:
        try:
            lumber_curr = int(lumber.split('/')[0])
            lumber_cap = int(lumber.split('/')[1])
            storage[ResourceType.LUMBER] = (lumber_curr, lumber_cap)
        except (IndexError, ValueError) as err:
            logger.error('In get_storage: Lumber storage does not respect pattern. Error: %s' % err)
    else:
        logger.error('In get_storage: SWS.getElementAttribute() failed')
    # Extract clay storage
    clay = sws.getElementAttribute(XPATH.PRODUCTION_CLAY, Attr.TEXT)
    if clay:
        try:
            clay_curr = int(clay.split('/')[0])
            clay_cap = int(clay.split('/')[1])
            storage[ResourceType.CLAY] = (clay_curr, clay_cap)
        except (IndexError, ValueError) as err:
            logger.error('In get_storage: Clay storage does not respect pattern. Error: %s' % err)
    else:
        logger.error('In get_storage: SWS.getElementAttribute() failed')
    # Extract iron storage
    iron = sws.getElementAttribute(XPATH.PRODUCTION_IRON, Attr.TEXT)
    if iron:
        try:
            iron_curr = int(iron.split('/')[0])
            iron_cap = int(iron.split('/')[1])
            storage[ResourceType.IRON] = (iron_curr, iron_cap)
        except (IndexError, ValueError) as err:
            logger.error('In get_storage: Iron storage does not respect pattern. Error: %s' % err)
    else:
        logger.error('In get_storage: SWS.getElementAttribute() failed')
    # Extract crop storage
    crop = sws.getElementAttribute(XPATH.PRODUCTION_CROP, Attr.TEXT)
    if crop:
        try:
            crop_curr = int(crop.split('/')[0])
            crop_cap = int(crop.split('/')[1])
            storage[ResourceType.CROP] = (crop_curr, crop_cap)
        except (IndexError, ValueError) as err:
            logger.error('In get_storage: Crop storage does not respect pattern. Error: %s' % err)
    else:
        logger.error('In get_storage: SWS.getElementAttribute() failed')
    return storage


def get_production(sws: SWS):
    """
    Gets for production for each resource for current village.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
    
    Returns:
        - Dictionary mapping each resource to its production value.
    """
    production = {}
    # Extract lumber production
    lumber = sws.getElementAttribute(XPATH.PRODUCTION_LUMBER, Attr.TITLE)
    if lumber:
        try:
            production[ResourceType.LUMBER] = int(lumber)
        except ValueError as err:
            logger.error('In get_production: Failed to convert to int. Error: %s' % err)
    else:
        logger.error('In get_production: SWS.getElementAttribute() failed')
    # Extract clay production
    clay = sws.getElementAttribute(XPATH.PRODUCTION_CLAY, Attr.TITLE)
    if clay:
        try:
            production[ResourceType.CLAY] = int(clay)
        except ValueError as err:
            logger.error('In get_production: Failed to convert to int. Error: %s' % err)
    else:
        logger.error('In get_production: SWS.getElementAttribute() failed')
    # Extract iron production
    iron = sws.getElementAttribute(XPATH.PRODUCTION_IRON, Attr.TITLE)
    if iron:
        try:
            production[ResourceType.IRON] = int(iron)
        except ValueError as err:
            logger.error('In get_production: Failed to convert to int. Error: %s' % err)
    else:
        logger.error('In get_production: SWS.getElementAttribute() failed')
    # Extract crop production
    crop = sws.getElementAttribute(XPATH.PRODUCTION_CROP, Attr.TITLE)
    if crop:
        try:
            production[ResourceType.CROP] = int(crop)
        except ValueError as err:
            logger.error('In get_production: Failed to convert to int. Error: %s' % err)
    else:
        logger.error('In get_production: SWS.getElementAttribute() failed')
    return production


# Multi village
def multi_villages_status(sws: SWS):
    """
    Checks if the user has multiple villages.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - True if the account has multiple villages, False otherwise.
    """
    return sws.isVisible(XPATH.ALL_VILLAGES_LINKS)


def get_all_villages_name(sws: SWS):
    """
    Gets the name of all villages:

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - List of strings.
    """
    ret = []
    if multi_villages_status(sws):
        ret = sws.getElementsAttribute(XPATH.ALL_VILLAGES_LINKS, Attr.TEXT)
    else:
        logger.warning('In get_all_villages_name: multi_villages_status() failed')
    return ret


def get_current_village(sws: SWS):
    """
    Gets the currently selected village.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - String with village name if operation was successful, None otherwise.
    """
    ret = None
    if multi_villages_status(sws):
        selectedVillage = sws.getElementAttribute(XPATH.SELECTED_VILLAGE, Attr.TEXT)
        if selectedVillage:
            ret = selectedVillage
        else:
            logger.error('In get_current_village: SWS.getElementAttribute() failed')
    else:
        logger.warning('In get_current_village: multi_villages_status() failed')
    return ret


def select_village(sws: SWS, villageName: str):
    """
    Attempts to select a village.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - villageName (str): Desired village.

    Returns:
        - True if operation was successful, None otherwise.
    """
    ret = False
    if multi_villages_status(sws):
        if sws.clickElement(XPATH.SELECT_VILLAGE % villageName, refresh=True):
            ret = True
        else:
            logger.error(f'In select_village: SWS.clickElement() failed')
    else:
        logger.warning('In select_village: multi_villages_status() failed')
    return ret


def village_send_goods(sws: SWS, villageName: str, ammount: list):
    """
    Sends goods to desired village.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - villageName (str): Desired village.
        - ammount (list): Contains 4 integers denoting how much resources to send.

    Returns:
        - True if operation was successful, None otherwise.
    """
    return True


def village_send_troops(sws: SWS, villageName: str):
    """
    Will send goods to desired village.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - villageName (str): Desired village.
        - ammount (list): Contains 4 integers denoting how much resources to send.

    Returns:
        - True if operation was successful, None otherwise.
    """
    return True


# Screen
# Current screen checking
def is_screen_overview(sws: SWS):
    """
    Checks if the current screen is Overview.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __get_current_screen(sws) == Screen.OVERVIEW


def is_screen_village(sws: SWS):
    """
    Checks if the current screen is Village.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __get_current_screen(sws) == Screen.VILLAGE


def is_screen_map(sws: SWS):
    """
    Checks if the current screen is Map.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __get_current_screen(sws) == Screen.MAP


def is_screen_statistics(sws: SWS):
    """
    Checks if the current screen is Statistics.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __get_current_screen(sws) == Screen.STATISTICS


def is_screen_messages(sws: SWS):
    """
    Checks if the current screen is Messages.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __get_current_screen(sws) == Screen.MESSAGES


def is_screen_reports(sws: SWS):
    """
    Checks if the current screen is Reports.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __get_current_screen(sws) == Screen.REPORTS


def is_screen_profile(sws: SWS):
    """
    Checks if the current screen is Profile.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __get_current_screen(sws) == Screen.PROFILE


# Change current screen
def move_to_overview(sws: SWS, forced: bool = False):
    """
    Changes current screen to Overview.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - forced (bool): If true will refresh the page.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __move_to_screen(sws, Screen.OVERVIEW, forced)


def move_to_village(sws: SWS, forced: bool = False):
    """
    Changes current screen to Village.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - forced (bool): If true will refresh the page.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __move_to_screen(sws, Screen.VILLAGE, forced)


def move_to_map(sws: SWS, forced: bool = False):
    """
    Changes current screen to Map.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - forced (bool): If true will refresh the page.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __move_to_screen(sws, Screen.MAP, forced)


def move_to_statistics(sws: SWS, forced: bool = False):
    """
    Changes current screen to Statistics.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - forced (bool): If true will refresh the page.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __move_to_screen(sws, Screen.STATISTICS, forced)


def move_to_reports(sws: SWS, forced: bool = False):
    """
    Changes current screen to Reports.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - forced (bool): If true will refresh the page.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __move_to_screen(sws, Screen.REPORTS, forced)


def move_to_messages(sws: SWS, forced: bool = False):
    """
    Changes current screen to Messages.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - forced (bool): If true will refresh the page.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __move_to_screen(sws, Screen.MESSAGES, forced)


def move_to_profile(sws: SWS, forced: bool = False):
    """
    Changes current screen to Profile.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - forced (bool): If true will refresh the page.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __move_to_screen(sws, Screen.PROFILE, forced)
