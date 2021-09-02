from Framework.screen.Login import ACCOUNT
import re
from enum import IntEnum, Enum
from Framework.utils.Constants import Tribe, get_ACCOUNT, get_XPATHS
from Framework.utils.Logger import get_projectLogger
from Framework.utils.SeleniumUtils import get, getCurrentUrl, isVisible, getElementAttribute, clickElement


logger = get_projectLogger()
ACCOUNT = get_ACCOUNT()
XPATHS = get_XPATHS()
TRIBE = None


class LevelUpMode(IntEnum):
    OFF = 0
    ON = 1


class Screens(Enum):
    OVERVIEW = 'village1'
    VILLAGE = 'village2'
    MAP = 'map'
    STATS = 'statistics'


def getTribe(driver):
    """
    Gets the tribe.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.

    Returns:
        - Tribe if operation was successful, None otherwise.
    """
    global TRIBE
    if not TRIBE:
        if isVisible(driver, XPATHS.ROMAN_TASK_MASTER):
            TRIBE = Tribe.ROMANS
        elif isVisible(driver, XPATHS.TEUTON_TASK_MASTER):
            TRIBE = Tribe.TEUTONS
        elif isVisible(driver, XPATHS.GAUL_TASK_MASTER):
            TRIBE = Tribe.GAULS
        else:
            logger.warning('In function getTribe: Could not identify the tribe by task manager')
    if not TRIBE:
        num = int(re.search('s[0-9]', getCurrentUrl(driver)).group()[1])
        initialURL = getCurrentUrl(driver)
        PROFILE_URL = f'{ACCOUNT.URL}profile.php' % num
        if get(driver, PROFILE_URL):
            propList = ['//*[@class="details"]', './/*[contains(text(), "Tribe:")]/..']
            text = getElementAttribute(driver, propList, 'text')
            if text:
                text = text[0].split()[-1].upper()
                for tr in Tribe:
                    if tr.name == text:
                        TRIBE = tr
                        break
                else:
                    logger.error('In function getTribe: Tribe could not be determined')
                if not get(driver, initialURL):
                    TRIBE = None
                    logger.error('In function getTribe: Could not get back to initial page')
            else:
                logger.error('In function getTribe: Could not find text element')
        else:
            logger.error('In function getTribe: Could not get profile page')
    return TRIBE


def get_current_screen(driver):
    """
    Tells which of the following screens is active:
      - Overview
      - Village
      - Map
      - Statistics
      - None, if you are inside a menu i.e. Constructing a new building.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.

    Returns:
        - Current screen if operation was successful, None otherwise.
    """
    for view in Screens:
        if view.value in driver.current_url:
            return view
    return None


def get_level_up_mode(driver):
    """
    Checks level up mode status.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.

    Returns:
        - LevelUpMode if operation was successful, None otherwise.
    """
    status = None
    currentView = get_current_screen(driver)
    if currentView == Screens.OVERVIEW or currentView == Screens.VILLAGE:
        coneTitle = getElementAttribute(driver, XPATHS.LEVEL_UP_CONE, 'title')
        if coneTitle:
            coneTitle = coneTitle[0]
            if "enable" in coneTitle:
                status = LevelUpMode.OFF
            elif 'disable' in coneTitle:
                status = LevelUpMode.ON
            else:
                logger.error('In function get_level_up_mode: Unknown cone status')
        else:
            logger.error('In function get_level_up_mode: Level up cone not found')
    else:
        logger.error('In function get_level_up_mode: Level up mode is available just \
            in overview and village')
    return status


def set_level_up_mode(driver, levelUpMode):
    """
    Sets level up mode.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.
        - levelUpMode (LevelUpMode): Will set level up mode to this.

    Returns:
        - True if the operation was successful, False otherwise.
    """
    status = False
    if isinstance(levelUpMode, LevelUpMode):
        currentView = get_current_screen(driver)
        if currentView == Screens.OVERVIEW or currentView == Screens.VILLAGE:
            coneTitle = getElementAttribute(driver, XPATHS.LEVEL_UP_CONE, 'title')
            if coneTitle:
                coneTitle = coneTitle[0]
                if (levelUpMode == LevelUpMode.ON and "enable" in coneTitle) or \
                        (levelUpMode == LevelUpMode.OFF and "disable" in coneTitle):
                    if clickElement(driver, XPATHS.LEVEL_UP_CONE, refresh=True):
                        status = True
                    else:
                        logger.error('In function set_level_up_mode: Failed to click LEVEL_UP_CONE')
                else:
                    status = True
            else:
                logger.error('In function set_level_up_mode: Cone title could not be found')
        else:
            logger.error('In function set_level_up_mode: Level up mode is available just \
                in overview and village')
    else:
        logger.error('In function set_level_up_mode: Invalid parameter levelUpMode')
    return status


def __move_to_screen(driver, screen, forced=False):
    """
    Ensures that the current view is the desired screen.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.
        - screen (Screen): Desired screen.
        - forced (Boolean): If True will refresh the screen even tho
            is the desired one, False by default

    Returns:
        - True if the operation was successful, False otherwise.
    """
    URLS = {
        Screens.OVERVIEW: f'{ACCOUNT.URL}village1.php',
        Screens.VILLAGE: f'{ACCOUNT.URL}village2.php',
        Screens.MAP: f'{ACCOUNT.URL}map.php',
        Screens.STATS: f'{ACCOUNT.URL}statistics.php'
    }
    status = False
    if isinstance(screen, Screens):
        if screen != get_current_screen(driver) or forced:
            if get(driver, URLS[screen]):
                status = True
            else:
                logger.error('In function __move_to_screen: Failed to move to screen')
        else:
            status = True
    else:
        logger.error('In function __move_to_screen: Invalid parameter screen')
    return status


def move_to_overview(driver, forced=False):
    """
    Changes current screen to overview.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.
        - forced (Boolean): If true will refresh the page.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __move_to_screen(driver, Screens.OVERVIEW, forced)


def move_to_village(driver, forced=False):
    """
    Changes current screen to village.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.
        - forced (Boolean): If true will refresh the page.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __move_to_screen(driver, Screens.VILLAGE, forced)


def move_to_map(driver, forced=False):
    """
    Changes current screen to map.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.
        - forced (Boolean): If true will refresh the page.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __move_to_screen(driver, Screens.MAP, forced)


def move_to_stats(driver, forced=False):
    """
    Changes current screen to stats.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.
        - forced (Boolean): If true will refresh the page.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __move_to_screen(driver, Screens.STATS, forced)


def get_storage(driver):
    """
    Checks for storage for each resource.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.
    
    Returns:
        - List of 4 Ints if operation was successful, None otherwise.
    """
    storage = []
    if isVisible(driver, XPATHS.PRODUCTION_LUMBER):
        lumber = getElementAttribute(driver, XPATHS.PRODUCTION_LUMBER, 'text')
        if lumber:
            lumber = lumber[0].split('/')
            storage.append((int(lumber[0]), int(lumber[1])))
    if isVisible(driver, XPATHS.PRODUCTION_CLAY):
        clay =  getElementAttribute(driver, XPATHS.PRODUCTION_CLAY, 'text')
        if clay:
            clay = clay[0].split('/')
            storage.append((int(clay[0]), int(clay[1])))
    if isVisible(driver, XPATHS.PRODUCTION_IRON):
        iron = getElementAttribute(driver, XPATHS.PRODUCTION_IRON, 'text')
        if iron:
            iron = iron[0].split('/')
            storage.append((int(iron[0]), int(iron[1])))
    if isVisible(driver, XPATHS.PRODUCTION_CROP):
        crop = getElementAttribute(driver, XPATHS.PRODUCTION_CROP, 'text')
        if crop:
            crop = crop[0].split('/')
            storage.append((int(crop[0]), int(crop[1])))
    if len(storage) != 4:
        storage = None
        logger.error('In function get_storage: Less than 4 values found')
    return storage


def get_production(driver):
    """
    Checks for production for each resource.

    Parameters:
        - driver (WebDriver): Used to interact with the webpage.
    
    Returns:
        - List of 4 Ints if operation was successful, None otherwise.
    """
    production = []
    lumber = getElementAttribute(driver, XPATHS.PRODUCTION_LUMBER, 'title')
    if lumber:
        production.append(int(lumber[0]))
    clay = getElementAttribute(driver, XPATHS.PRODUCTION_CLAY, 'title')
    if clay:
        production.append(int(clay[0]))
    iron = getElementAttribute(driver, XPATHS.PRODUCTION_IRON, 'title')
    if iron:
        production.append(int(iron[0]))
    crop = getElementAttribute(driver, XPATHS.PRODUCTION_CROP, 'title')
    if crop:
        production.append(int(crop[0]))
    if len(production) != 4:
        production = None
        logger.error('In function get_production: Less than 4 values found')
    return production
