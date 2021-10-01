from enum import Enum
from Framework.screen.HomeUI import is_screen_overview, is_screen_village, move_to_overview
from Framework.utility.Constants import get_XPATH, get_projectLogger
from Framework.utility.SeleniumWebScraper import SWS, Attr


# Project constants
logger = get_projectLogger()
XPATH = get_XPATH()


def get_village_name(sws: SWS):
    """
    Gets village name in overview or village screen.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - String with village name if operation was successful, None otherwise.
    """
    ret = None
    if move_to_overview(sws):
        villageName = sws.getElementAttribute(XPATH.VILLAGE_NAME, Attr.TEXT)
        if villageName:
            ret = villageName
        else:
            logger.error('In get_village_name: SWS.getElementAttribute() failed')
    else:
        logger.warning('In get_village_name: move_to_overview() failed')
    return ret
