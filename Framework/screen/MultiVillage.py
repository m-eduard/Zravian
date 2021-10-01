from Framework.utility.Constants import get_XPATH, get_projectLogger
from Framework.utility.SeleniumWebScraper import SWS, Attr


# Project constants
logger = get_projectLogger()
XPATH = get_XPATH()


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
        - [str] if operation is successful, None otherwise.
    """
    ret = None
    if multi_villages_status(sws):
        villageNames = sws.getElementsAttribute(XPATH.ALL_VILLAGES_LINKS, Attr.TEXT)
        if villageNames:
            ret = villageNames
        else:
            logger.error('In get_all_villages_name: Failed to extract villages name')
    else:
        logger.warning('In get_all_villages_name: multi_villages_status() failed')
    return ret


def get_current_village(sws: SWS):
    """
    Gets the currently selected village.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - str if operation was successful, None otherwise.
    """
    ret = None
    if multi_villages_status(sws):
        selectedVillage = sws.getElementAttribute(XPATH.SELECTED_VILLAGE, Attr.TEXT)
        if selectedVillage:
            ret = selectedVillage
        else:
            logger.error('In get_current_village: Failed to get selected village')
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
        if villageName in get_all_villages_name(sws):
            if sws.clickElement(XPATH.SELECT_VILLAGE % villageName, refresh=True):
                if get_current_village(sws) == villageName:
                    ret = True
                else:
                    logger.error(f'In select_village: Operation failed {villageName} was not selected')
            else:
                logger.error(f'In select_village: Failed to click on village option')
        else:
            logger.warning(f'In select_village: {villageName} not in villages')
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
