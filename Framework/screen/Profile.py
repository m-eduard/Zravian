from Framework.utility.Constants import get_XPATH
from Framework.utility.Logger import get_projectLogger
from Framework.utility.SeleniumUtils import SWS


# Project constants
logger = get_projectLogger()
XPATH = get_XPATH()


def press_edit_profile(sws : SWS):
    """
    Presses edit profile in profile view.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - True if operation was successful, False otherwise.
    """
    return sws.clickElement(XPATH.EDIT_PROFILE, refresh=True)


def press_ok_button(sws : SWS):
    """
    Presses ok button.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - True if operation was successful, False otherwise.    
    """
    return sws.clickElement(XPATH.PROFILE_OK_BTN, refresh=True)


def add_to_description(sws : SWS, text : str):
    """
    Adds text to description.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - text (str): String to insert.

    Returns:
        - True if operation was successful, False otherwise.
    """
    return sws.sendKeys(XPATH.PROFILE_DESCR, text)


def change_village_name(sws : SWS, initialName : str, newName : str):
    """
    Changes a village name.

    Parameters:
        - sws (SWS): Selenium Web Scraper.
        - initialName (str): Village name to be updated.
        - newName (str): Village name after update.

    Returns:
        - True if operation was successful, False otherwise.
    """
    ret = False
    if sws.isVisible(XPATH.STRING_ON_SCREEN % initialName):
        if sws.sendKeys(XPATH.STRING_ON_SCREEN % initialName, None):
            if sws.sendKeys(XPATH.STRING_ON_SCREEN % initialName, newName):
                ret = True
            else:
                logger.error('In change_village_name: Failed to insert new name')
        else:
            logger.error('In change_village_name: Failed to clear text box')
    else:
        logger.error('In change_village_name: Failed to find old name')
    return ret
    

