import re
from enum import IntEnum, Enum
from Framework.utility.Constants import ResourceType, Server, get_XPATH
from Framework.utility.Logger import get_projectLogger
from Framework.utility.SeleniumUtils import SWS


# Project constants
logger = get_projectLogger()
XPATH = get_XPATH()


class Screen(Enum):
    OVERVIEW = 'village1.php'
    VILLAGE = 'village2.php'
    MAP = 'map.php'
    STATISTICS = 'statistics.php'
    PROFILE = 'profile.php'
    MESSAGES = 'msg.php'
    REPORTS = 'report.php'


class LevelUpMode(IntEnum):
    OFF = 0
    ON = 1


class InstructionsSearchItem(Enum):
    COSTS = XPATH.INSTRUCTIONS_COSTS


# Utils
def __get_current_screen(sws : SWS):
    """
    Tells which of the following screen is active:
      - Overview
      - Village
      - Map
      - Statistics
      - None, if you are inside a menu i.e. Constructing a new building.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - Current screen if operation was successful, None otherwise.
    """
    for screen in Screen:
        if screen.value in sws.getCurrentUrl():
            return screen
    return None


def __move_to_screen(sws : SWS, screen : Screen, forced : bool = False):
    """
    Ensures that the current screen is the desired screen.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - screen (Screen): Desired screen.
        - forced (bool): If True will refresh the screen even tho
            is the desired one, False by default

    Returns:
        - True if the operation was successful, False otherwise.
    """
    ret = False
    BASE_URL = sws.getCurrentUrl().rsplit("/", 1)[0] + '/'
    if screen != __get_current_screen(sws) or forced:
        if sws.get(BASE_URL + screen.value):
            ret = True
        else:
            logger.error('In __move_to_screen: Failed to move to screen')
    else:
        ret = True
    return ret


def __search_in_instructions(sws : SWS, locators : list, item : InstructionsSearchItem):
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
    INSTRUCTIONS_MENU = 'Instructions'
    INSTRUCTIONS_IFRAME = 'Frame'
    # Open instructions menu
    if sws.clickElement(XPATH.STRING_ON_SCREEN % INSTRUCTIONS_MENU):
        sws.enter_iframe(INSTRUCTIONS_IFRAME)
        for locator in locators:
            if sws.isVisible(XPATH.STRING_ON_SCREEN % locator):
                if not sws.clickElement(XPATH.STRING_ON_SCREEN % locator):
                    logger.error(f'In __search_in_instructions: Failed to click {locator}')
                    break
            else:
                logger.error(f'In __search_in_instructions: Failed to find {locator}')
                break
        else:
            ret = sws.getElementAttribute(item.value, 'text')
        sws.exit_iframe()
    else:
        logger.error('In __search_in_instructions: Failed to open instructions')
    return ret


# User UI
def press_continue_btn(sws : SWS):
    """
    Presses the continue button after first ever login.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - True if the operation was successful, False otherwise.
    """
    ret = False
    CONTINUE_BTN_TEXT = 'Continue'
    if sws.clickElement(XPATH.STRING_ON_SCREEN % CONTINUE_BTN_TEXT, refresh=True, waitFor=True):
        ret = True
    else:
        logger.error('In press_continue_btn: Failed to press continue button')
    return ret


def get_server(sws : SWS):
    """
    Returns the current server.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - Current server if operation is successful, None otherwise.
    """
    ret = None
    try:
        serverURL = re.match(r'(.*)\/(.*)', sws.getCurrentUrl()).group(1) + '/'
        for server in Server:
            if server.value == serverURL:
                ret = server
                break
        else:
            logger.error(f'In get_server: No server matched {sws.getCurrentUrl()}')
    except AttributeError as err:
        logger.error(f'In get_server: Regex failed to get server: {err}')
    return ret


def get_level_up_mode(sws : SWS):
    """
    Checks level up mode status.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - LevelUpMode if operation was successful, None otherwise.
    """
    status = None
    if is_screen_overview(sws) or is_screen_village(sws):
        coneTitle = sws.getElementAttribute(XPATH.LEVEL_UP_CONE, 'title')
        if coneTitle:
            if "enable" in coneTitle:
                status = LevelUpMode.OFF
            elif 'disable' in coneTitle:
                status = LevelUpMode.ON
            else:
                logger.error('In get_level_up_mode: Unknown cone status')
        else:
            logger.error('In get_level_up_mode: Level up cone not found')
    else:
        logger.error('In get_level_up_mode: Level up mode is available just' \
            'in overview and village')
    return status


def set_level_up_mode(sws : SWS, levelUpMode : LevelUpMode):
    """
    Sets level up mode.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - levelUpMode (LevelUpMode): Will set level up mode to this.

    Returns:
        - True if the operation was successful, False otherwise.
    """
    status = False
    if is_screen_overview(sws) or is_screen_village(sws):
        coneTitle = sws.getElementAttribute(XPATH.LEVEL_UP_CONE, 'title')
        if coneTitle:
            if (levelUpMode == LevelUpMode.ON and "enable" in coneTitle) or \
                    (levelUpMode == LevelUpMode.OFF and "disable" in coneTitle):
                if sws.clickElement(XPATH.LEVEL_UP_CONE, refresh=True):
                    status = True
                else:
                    logger.error('In set_level_up_mode: Failed to click LEVEL_UP_CONE')
            else:
                status = True
        else:
            logger.error('In set_level_up_mode: Cone title could not be found')
    else:
        logger.error('In set_level_up_mode: Level up mode is available just \
            in overview and village')
    return status


def instructions_get_costs(sws : SWS, locators : list):
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
        ret = costsText.split('\n')[1].split('|')[:-1]
    else:
        logger.error('In instructions_get_costs: Failed to find required page and get costs')
    return ret


# Village dependent
def get_village_name(sws : SWS):
    """
    Gets village name in overview or village screen.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - String with village name if operation was successful, None otherwise.
    """
    ret = None
    if is_screen_overview(sws) or is_screen_village(sws):
        villageName = sws.getElementAttribute(XPATH.VILLAGE_NAME, 'text')
        if villageName:
            ret = villageName
        else:
            logger.error('In get_village_name: Failed to get village name from element')
    else:
        logger.error('In get_village_name: Unable to get village name in this screen')
    return ret


def get_storage(sws : SWS):
    """
    Checks for storage for each resource for current village.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
    
    Returns:
        - Dictionary mapping each resource field to tuple.
    """
    storage = {}
    # Extract lumber storage
    lumber = sws.getElementAttribute(XPATH.PRODUCTION_LUMBER, 'text')
    if lumber:
        try:
            lumber_curr = int(lumber.split('/')[0])
            lumber_cap = int(lumber.split('/')[1])
            storage[ResourceType.LUMBER] = (lumber_curr, lumber_cap)
        except ValueError as e:
            logger.error('In get_storage: Failed to convert to int. Error: %s' % e)
    else:
        logger.error('In get_storage: Failed to get lumber storage')
    # Extract clay storage
    clay = sws.getElementAttribute(XPATH.PRODUCTION_CLAY, 'text')
    if clay:
        try:
            clay_curr = int(clay.split('/')[0])
            clay_cap = int(clay.split('/')[1])
            storage[ResourceType.CLAY] = (clay_curr, clay_cap)
        except ValueError as e:
            logger.error('In get_storage: Failed to convert to int. Error: %s' % e)
    else:
        logger.error('In get_storage: Failed to get clay storage')
    # Extract iron storage
    iron = sws.getElementAttribute(XPATH.PRODUCTION_IRON, 'text')
    if iron:
        try:
            iron_curr = int(iron.split('/')[0])
            iron_cap = int(iron.split('/')[1])
            storage[ResourceType.IRON] = (iron_curr, iron_cap)
        except ValueError as e:
            logger.error('In get_storage: Failed to convert to int. Error: %s' % e)
    else:
        logger.error('In get_storage: Failed to get iron storage')
    # Extract crop storage
    crop = sws.getElementAttribute(XPATH.PRODUCTION_CROP, 'text')
    if crop:
        try:
            crop_curr = int(crop.split('/')[0])
            crop_cap = int(crop.split('/')[1])
            storage[ResourceType.CROP] = (crop_curr, crop_cap)
        except ValueError as e:
            logger.error('In get_storage: Failed to convert to int. Error: %s' % e)
    else:
        logger.error('In get_storage: Failed to get crop storage')
    return storage


def get_production(sws : SWS):
    """
    Checks for production for each resource for current village.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
    
    Returns:
        - Dictionary mapping each resource to its production value.
    """
    production = {}
    # Extract lumber production
    lumber = sws.getElementAttribute(XPATH.PRODUCTION_LUMBER, 'title')
    if lumber:
        try:
            production[ResourceType.LUMBER] = int(lumber)
        except ValueError as e:
            logger.error('In get_production: Failed to convert to int. Error: %s' % e)
    else:
        logger.error('In get_storage: Failed to get lumber storage')
    # Extract clay production
    clay = sws.getElementAttribute(XPATH.PRODUCTION_CLAY, 'title')
    if clay:
        try:
            production[ResourceType.CLAY] = int(clay)
        except ValueError as e:
            logger.error('In get_production: Failed to convert to int. Error: %s' % e)
    else:
        logger.error('In get_storage: Failed to get clay storage')
    # Extract iron production
    iron = sws.getElementAttribute(XPATH.PRODUCTION_IRON, 'title')
    if iron:
        try:
            production[ResourceType.IRON] = int(iron)
        except ValueError as e:
            logger.error('In get_production: Failed to convert to int. Error: %s' % e)
    else:
        logger.error('In get_storage: Failed to get iron storage')
    # Extract crop production
    crop = sws.getElementAttribute(XPATH.PRODUCTION_CROP, 'title')
    if crop:
        try:
            production[ResourceType.CROP] = int(crop)
        except ValueError as e:
            logger.error('In get_production: Failed to convert to int. Error: %s' % e)
    else:
        logger.error('In get_storage: Failed to get crop storage')
    return production


# Multi village
def get_all_villages_name(sws : SWS):
    """
    Gets the name of all villages:

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - List of strings.
    """
    villages = sws.getElementsAttribute(XPATH.ALL_VILLAGES_LINKS, 'text')
    return villages


def get_current_village(sws : SWS):
    """
    Gets the currently selected village.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - String with village name if operation was successful, None otherwise.
    """
    ret = None
    selectedVillage = sws.getElementAttribute(XPATH.SELECTED_VILLAGE, 'text')
    if selectedVillage:
        ret = selectedVillage
    else:
        logger.error('In get_current_village: Failed to get selected village')
    return ret


def select_village(sws : SWS, villageName : str):
    """
    Attempts to select a village.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - villageName (str): Desired village.

    Returns:
        - True if operation was successful, None otherwise.
    """
    ret = False
    if sws.clickElement(XPATH.SELECT_VILLAGE % villageName, refresh=True):
        if get_village_name(sws) == villageName:
            ret = True
        else:
            logger.error('In select_village: New village name does not correspond')
    else:
        logger.error(f'In select_village: Failed to move to village {villageName}')
    return ret


def village_send_goods(sws : SWS, villageName : str, ammount : list):
    """
    Will send goods to desired village.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - villageName (str): Desired village.
        - ammount (list): Contains 4 integers denoting how much resources to send.

    Returns:
        - True if operation was successful, None otherwise.
    """
    ret = False
    if len(ammount) == 4 and all(isinstance(elem, int) for elem in ammount):
        if get_current_village(sws) != villageName:
            if sws.clickElement(XPATH.SEND_GOODS % villageName, refresh=True):
                if sws.sendKeys(XPATH.SEND_LUMBER_INPUT_BOX, str(ammount[0])):
                    pass
                else:
                    logger.error('In village_send_goods: Failed to send lumber')
            else:
                logger.warning('In village_send_goods: Failed to open send resources page.'
                    'Ensure marketplace is built')
        else:
            logger.warning('In village_send_goods: Unable to send goods to the same village')
    else:
        logger.error('In village_send_goods: Ammount must contain exactly 4 integers')
    return ret


def village_send_troops(sws : SWS, villageName : str):
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
def is_screen_overview(sws : SWS):
    """
    Checks if the current screen is Overview.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __get_current_screen(sws) == Screen.OVERVIEW


def is_screen_village(sws : SWS):
    """
    Checks if the current screen is Village.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __get_current_screen(sws) == Screen.VILLAGE


def is_screen_map(sws : SWS):
    """
    Checks if the current screen is Map.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __get_current_screen(sws) == Screen.MAP


def is_screen_statistics(sws : SWS):
    """
    Checks if the current screen is Statistics.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __get_current_screen(sws) == Screen.STATISTICS


def is_screen_messages(sws : SWS):
    """
    Checks if the current screen is Messages.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __get_current_screen(sws) == Screen.MESSAGES


def is_screen_reports(sws : SWS):
    """
    Checks if the current screen is Reports.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __get_current_screen(sws) == Screen.REPORTS


def is_screen_profile(sws : SWS):
    """
    Checks if the current screen is Profile.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __get_current_screen(sws) == Screen.PROFILE


# Change current screen
def move_to_overview(sws : SWS, forced : bool = False):
    """
    Changes current screen to Overview.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - forced (bool): If true will refresh the page.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __move_to_screen(sws, Screen.OVERVIEW, forced)


def move_to_village(sws : SWS, forced : bool = False):
    """
    Changes current screen to Village.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - forced (bool): If true will refresh the page.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __move_to_screen(sws, Screen.VILLAGE, forced)


def move_to_map(sws : SWS, forced : bool = False):
    """
    Changes current screen to Map.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - forced (bool): If true will refresh the page.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __move_to_screen(sws, Screen.MAP, forced)


def move_to_statistics(sws : SWS, forced : bool = False):
    """
    Changes current screen to Statistics.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - forced (bool): If true will refresh the page.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __move_to_screen(sws, Screen.STATISTICS, forced)


def move_to_reports(sws : SWS, forced : bool = False):
    """
    Changes current screen to Reports.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - forced (bool): If true will refresh the page.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __move_to_screen(sws, Screen.REPORTS, forced)


def move_to_messages(sws : SWS, forced : bool = False):
    """
    Changes current screen to Messages.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - forced (bool): If true will refresh the page.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __move_to_screen(sws, Screen.MESSAGES, forced)


def move_to_profile(sws : SWS, forced : bool = False):
    """
    Changes current screen to Profile.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - forced (bool): If true will refresh the page.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __move_to_screen(sws, Screen.PROFILE, forced)
