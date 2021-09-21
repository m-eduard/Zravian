from Framework.utility.Constants import get_XPATH
from Framework.utility.Logger import get_projectLogger
from Framework.utility.SeleniumUtils import SWS
from Framework.screen.Views import Views, get_current_view


# Project constants
logger = get_projectLogger()
XPATH = get_XPATH()


def get_village_coordinates(sws : SWS, villageName : str):
    """
    Gets a village coordinates from main map view.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - List with 2 int representing coords.
    """
    ret = None
    if get_current_view(sws) == Views.MAP:
        if sws.isVisible(XPATH.VILLAGE_BY_NAME % villageName):
            altList = sws.getElementAttribute(XPATH.VILLAGE_BY_NAME % villageName, 'alt')
            if altList:
                coordsText = altList.split()[0]
                coords = coordsText[1:-1].split('|')
                coords = [''.join(x for x in c if x.isdigit()) for c in coords]
                if coords:
                    ret = [int(c) for c in coords]
                else:
                    logger.error('In get_village_coordinates: Coordinates text does not respect pattern')
            else:
                logger.error('In get_village_coordinates: Failed to get village "alt" attribute')
        else:
            logger.warning('In get_village_coordinates: Failed to find village')
    else:
        logger.error('In get_village_coordinates: View is not map')
    return ret


