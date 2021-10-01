from Framework.screen.HomeUI import move_to_overview, move_to_profile
from Framework.utility.Constants import Tribe, get_XPATH, get_projectLogger
from Framework.utility.SeleniumWebScraper import SWS, Attr


# Project constants
logger = get_projectLogger()
XPATH = get_XPATH()
TRIBE = None


def get_tribe(sws : SWS):
    """
    Gets the tribe from profile view.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - Tribe if operation was successful, None otherwise.
    """
    global TRIBE
    if not TRIBE:
        if move_to_profile(sws):
            text = sws.getElementAttribute(XPATH.PROFILE_TRIBE, Attr.TEXT)
            if text:
                text = text.split()[-1].upper()
                for tribe in Tribe:
                    if tribe.value == text:
                        TRIBE = tribe
                        break
                else:
                    logger.error('In get_tribe: Tribe could not be determined')
            else:
                logger.error('In get_tribe: SWS.getElementAttribute() failed')
        else:
            logger.error('In get_tribe: move_to_profile() failed')
    # Return to Overview
    if move_to_overview(sws) and TRIBE:
        logger.success('In get_tribe: Tribe identified')
    else:
        TRIBE = None
        logger.error('In get_tribe: move_to_overview() failed')
    return TRIBE


def get_capital(sws : SWS):
    """
    Gets the capital from profile view.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - String if the operation was successful, None otherwise.
    """
    ret = None
    if move_to_profile(sws):
        capital = sws.getElementAttribute(XPATH.PROFILE_CAPITAL, Attr.TEXT)
        if capital:
            ret = capital
        else:
            logger.error('In get_capital: SWS.getElementAttribute() failed')
    else:
        logger.error('In get_capital: move_to_profile() failed')
    # Return to Overview
    if move_to_overview(sws) and ret:
        logger.success('In get_capital: Capital identified')
    else:
        ret = None
        logger.error('In get_capital: Failed to move to Overview')
    return ret


def update_description(sws : SWS, text : str):
    """
    Adds text to description.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - text (str): String to insert.

    Returns:
        - True if operation was successful, False otherwise.
    """
    ret = False
    if move_to_profile(sws):
        if sws.clickElement(XPATH.EDIT_PROFILE, refresh=True):
            if sws.sendKeys(XPATH.PROFILE_DESCR, text):
                if sws.clickElement(XPATH.PROFILE_OK_BTN, refresh=True):
                    ret = True
                else:
                    logger.error('In update_description: SWS.clickElement() failed')
            else:
                logger.error('In update_description: SWS.sendKeys() failed')
        else:
            logger.error('In update_description: SWS.clickElement() failed')
    else:
        logger.error('In update_description: move_to_profile() failed')
    # Return to Overview
    if move_to_overview(sws) and ret:
        logger.success(f'In update_description: Description was updated to {text}')
    else:
        ret = False
        logger.error('In update_description: move_to_overview() failed')
    return ret


def update_village_name(sws : SWS, initialName : str, newName : str):
    """
    Updates a village name.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - initialName (str): Village name to be updated.
        - newName (str): Village name after update.

    Returns:
        - True if operation was successful, False otherwise.
    """
    ret = False
    if move_to_profile(sws):
        if sws.isVisible(XPATH.STRING_ON_SCREEN % initialName):
            if sws.sendKeys(XPATH.STRING_ON_SCREEN % initialName, None):
                if sws.sendKeys(XPATH.STRING_ON_SCREEN % initialName, newName):
                    ret = True
                else:
                    logger.error('In change_village_name: SWS.sendKeys() failed')
            else:
                logger.error('In change_village_name: SWS.sendKeys() failed')
        else:
            logger.error('In change_village_name: Failed to find old name')
    else:
        logger.error('In change_village_name: move_to_profile() failed')
    # Return to Overview
    if move_to_overview(sws) and ret:
        logger.success(f'In change_village_name: village {initialName} is now {newName}')
    else:
        ret = False
        logger.error('In change_village_name: move_to_overview() failed')
    return ret
