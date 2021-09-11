from enum import IntEnum
from Framework.screen.Views import Views, get_current_view, move_to_profile
from Framework.utility.Logger import get_projectLogger
from Framework.utility.Constants import Tribe, get_XPATH
from Framework.utility.SeleniumUtils import SWS


TRIBE = None
logger = get_projectLogger()
XPATH = get_XPATH()

class LevelUpMode(IntEnum):
    OFF = 0
    ON = 1


def getTribe(sws : SWS):
    """
    Gets the tribe.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - Tribe if operation was successful, None otherwise.
    """
    global TRIBE
    if not TRIBE:
        initialURL = sws.getCurrentUrl()
        if move_to_profile(sws):
            text = sws.getElementAttribute(XPATH.PROFILE_TRIBE, 'text')
            if text:
                text = text[0].split()[-1].upper()
                for tribe in Tribe:
                    if tribe.value == text:
                        TRIBE = tribe
                        break
                else:
                    logger.error('In getTribe: Tribe could not be determined')
                if not sws.get(initialURL):
                    TRIBE = None
                    logger.error('In getTribe: Could not get back to initial page')
            else:
                logger.error('In getTribe: Could not find text element')
        else:
            logger.error('In getTribe: Could not get profile view')
    return TRIBE


def get_level_up_mode(sws : SWS):
    """
    Checks level up mode status.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - LevelUpMode if operation was successful, None otherwise.
    """
    status = None
    currentView = get_current_view(sws)
    if currentView == Views.OVERVIEW or currentView == Views.VILLAGE:
        coneTitle = sws.getElementAttribute(XPATH.LEVEL_UP_CONE, 'title')
        if coneTitle:
            coneTitle = coneTitle[0]
            if "enable" in coneTitle:
                status = LevelUpMode.OFF
            elif 'disable' in coneTitle:
                status = LevelUpMode.ON
            else:
                logger.error('In get_level_up_mode: Unknown cone status')
        else:
            logger.error('In get_level_up_mode: Level up cone not found')
    else:
        logger.error('In get_level_up_mode: Level up mode is available just \
            in overview and village')
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
    currentView = get_current_view(sws)
    if currentView == Views.OVERVIEW or currentView == Views.VILLAGE:
        coneTitle = sws.getElementAttribute(XPATH.LEVEL_UP_CONE, 'title')
        if coneTitle:
            coneTitle = coneTitle[0]
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


def get_village_name(sws : SWS):
    """
    Gets village name in overview or village view.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - String with village name if operation was successful, None otherwise.
    """
    ret = None
    currentView = get_current_view(sws)
    if currentView == Views.OVERVIEW or currentView == Views.VILLAGE:
        villageName = sws.getElementAttribute(XPATH.VILLAGE_NAME, 'text')
        if villageName:
            ret = villageName[0]
        else:
            logger.error('In get_village_name: Failed to get village name')
    else:
        logger.error('In get_village_name: Unable to get village name in this view')
    return ret


def get_current_village(sws : SWS):
    """
    Gets the currently selected village.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - String with village name if operation was successful, None otherwise.
    """
    ret = None
    selectedVillage = sws.getElementsAttribute(XPATH.SELECTED_VILLAGE, 'text')
    if selectedVillage:
        ret = selectedVillage[0]
    else:
        logger.error('In get_current_village: Failed to get selected village')
    return ret


def get_all_villages_name(sws : SWS):
    """
    Gets the name of all villages:

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - List of strings.
    """
    villages = sws.getElementsAttribute(XPATH.ALL_VILLAGES_LINKS, 'text')
    villages = [village[0] for village in villages]
    return villages


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


def send_goods(sws : SWS, villageName : str, ammount : list):
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
                    logger.error('In send_goods: Failed to send lumber')
            else:
                logger.warning('In send_goods: Failed to open send resources page. Ensure marketplace is built')
        else:
            logger.warning('In send_goods: Unable to send goods to the same village')
    else:
        logger.error('In send_goods: Ammount must contain exactly 4 integers')
    return ret


# Village dependent
def get_storage(sws : SWS):
    """
    Checks for storage for each resource for current village.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
    
    Returns:
        - List of 4 Ints if operation was successful, None otherwise.
    """
    storage = []
    if sws.isVisible(XPATH.PRODUCTION_LUMBER):
        lumber = sws.getElementAttribute(XPATH.PRODUCTION_LUMBER, 'text')
        if lumber:
            lumber = lumber[0].split('/')
            storage.append((int(lumber[0]), int(lumber[1])))
    if sws.isVisible(XPATH.PRODUCTION_CLAY):
        clay =  sws.getElementAttribute(XPATH.PRODUCTION_CLAY, 'text')
        if clay:
            clay = clay[0].split('/')
            storage.append((int(clay[0]), int(clay[1])))
    if sws.isVisible(XPATH.PRODUCTION_IRON):
        iron = sws.getElementAttribute(XPATH.PRODUCTION_IRON, 'text')
        if iron:
            iron = iron[0].split('/')
            storage.append((int(iron[0]), int(iron[1])))
    if sws.isVisible(XPATH.PRODUCTION_CROP):
        crop = sws.getElementAttribute(XPATH.PRODUCTION_CROP, 'text')
        if crop:
            crop = crop[0].split('/')
            storage.append((int(crop[0]), int(crop[1])))
    if len(storage) != 4:
        storage = None
        logger.error('In get_storage: Less than 4 values found')
    return storage


def get_production(sws : SWS):
    """
    Checks for production for each resource for current village.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
    
    Returns:
        - List of 4 Ints if operation was successful, None otherwise.
    """
    production = []
    lumber = sws.getElementAttribute(XPATH.PRODUCTION_LUMBER, 'title')
    if lumber:
        production.append(int(lumber[0]))
    clay = sws.getElementAttribute(XPATH.PRODUCTION_CLAY, 'title')
    if clay:
        production.append(int(clay[0]))
    iron = sws.getElementAttribute(XPATH.PRODUCTION_IRON, 'title')
    if iron:
        production.append(int(iron[0]))
    crop = sws.getElementAttribute(XPATH.PRODUCTION_CROP, 'title')
    if crop:
        production.append(int(crop[0]))
    if len(production) != 4:
        production = None
        logger.error('In get_production: Less than 4 values found')
    return production

