from enum import Enum
import Framework.infrastructure.buildings as BD
from Framework.utility.Constants import BuildingType, get_XPATH, get_building_info, get_projectLogger
from Framework.utility.SeleniumWebScraper import SWS


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
    PLUS = 'plus.php'
    BUILDING_SITE = 'build.php?id='


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
        - True if operation was successful, False otherwise.
    """
    ret = False
    if screen != __get_current_screen(sws) or forced:
        # Current URL
        BASE_URL = sws.getCurrentUrl().rsplit("/", 1)[0] + '/'
        if sws.get(BASE_URL + screen.value):
            ret = True
        else:
            logger.error(f'In __move_to_screen: Failed to move to {screen.name}')
    else:
        ret = True
    return ret


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


def is_screen_plus(sws: SWS):
    """
    Checks if the current screen is Plus.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __get_current_screen(sws) == Screen.PLUS


def is_screen_building_site(sws: SWS):
    """
    Checks if the current screen is Building site.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __get_current_screen(sws) == Screen.BUILDING_SITE


def is_screen_menu_of(sws: SWS, bdType: BuildingType):
    """
    Checks if page corresponds to required building menu.

    Parameters:
        - sws (SWS): Used to interact with the webpage.
        - bdType (BuildingType): Denotes a type of building.

    Returns:
        - True if page title corresponds to building, False otherwise.
    """
    status = False
    if (bdType == BuildingType.EmptyPlace and sws.isVisible(XPATH.BUILDING_PAGE_EMPTY_TITLE)) or \
            bdType != BuildingType.EmptyPlace and \
            sws.isVisible(XPATH.BUILDING_PAGE_TITLE % get_building_info(bdType).name, waitFor=True):
        logger.info(f'In is_building_menu: Current screen is {get_building_info(bdType).name} menu')
        status = True
    else:
        logger.info(f'In is_building_menu: Current screen is not {get_building_info(bdType).name} menu')
    return status


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


def move_to_plus(sws: SWS, forced: bool = False):
    """
    Changes current screen to Plus.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - forced (bool): If true will refresh the page.

    Returns:
        - True if operation is successful, False otherwise.
    """
    ret = False
    if not is_screen_plus(sws) or forced:
        if sws.clickElement(XPATH.PLUS_MENU, refresh=True):
            ret = True
        else:
            logger.error('In move_to_plus: Failed to enter Plus menu')
    else:
        ret = True
    return ret


def enter_building_site(sws: SWS, index: int):
    """
    Enters a building site.

    Parameters:
        - sws (SWS): Used to interact with the webpage.
        - index (Int): Denotes building site index.

    Returns:
        - True if operation is successful, False otherwise.
    """
    status = False
    # Building site URL pattern
    BUILDING_SITE_PATTERN = 'build.php?id=%d'
    if index > 0 and index <= BD.LAST_BUILDING_SITE_VILLAGE:
        if index > 0 and index < BD.FIRST_BUILDING_SITE_VILLAGE:
            moveStatus = move_to_overview(sws)
        else:
            moveStatus = move_to_village(sws)
        if moveStatus:
            # Current URL
            BASE_URL = sws.getCurrentUrl().rsplit("/", 1)[0] + '/'
            if sws.get(BASE_URL + BUILDING_SITE_PATTERN % index):
                status = True
            else:
                logger.error('In enter_building_site: Failed to enter building by URL')
        else:
            logger.error('In enter_building_site: move_to_screen() failed')
    else:
        logger.error(f'In enter_building_site: Invalid parameter index {index}')
    return status


def enter_building(sws: SWS, bdType: BuildingType):
    """
    Enters the highest level building of requested type.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - bdType (BuildingType): Denotes a type of building.

    Returns:
        - True if operation was successful, False otherwise.    
    """
    status = False
    bdId = BD.find_building(sws, bdType)
    if bdId:
        if enter_building_site(sws, bdId.siteId) and is_screen_menu_of(sws, bdType):
            status = True
        else:
            logger.error(f'In enter_building: Failed to enter {get_building_info(bdType).name} at {bdId}')
    else:
        logger.warning(f'In enter_building: {get_building_info(bdType).name} not found. Ensure its constructed')
    return status
