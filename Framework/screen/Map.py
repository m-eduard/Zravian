from Framework.screen.Navigation import move_to_map, move_to_overview
from Framework.utility.Constants import get_XPATH, get_projectLogger
from Framework.utility.SeleniumWebScraper import SWS, Attr


# Project constants
logger = get_projectLogger()
XPATH = get_XPATH()


def get_village_coordinates(sws: SWS, villageName: str):
    """
    Gets a village coordinates from map view. Does not scroll in order to search for a village.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - List with 2 int representing coords.
    """
    ret = None
    if move_to_map(sws):
        if sws.isVisible(XPATH.VILLAGE_BY_NAME % villageName):
            altList = sws.getElementAttribute(XPATH.VILLAGE_BY_NAME % villageName, Attr.ALT)
            if altList:
                coordsText = altList.split()[0]
                coords = coordsText[1:-1].split('|')
                coords = [''.join(x for x in c if x.isdigit()) for c in coords]
                try:
                    ret = [int(c) for c in coords]
                except ValueError as err:
                    logger.error(f'In get_village_coordinates: Coordinates text does not respect pattern: {err}')
            else:
                logger.error('In get_village_coordinates: Failed to extract village coordinates')
        else:
            logger.warning('In get_village_coordinates: Failed to find village')
    else:
        logger.error('In get_village_coordinates: move_to_map() failed')
    # Return to Overview
    if move_to_overview(sws) and ret:
        logger.success(f'In get_village_coordinates: Coords of {villageName} were retireved')
    else:
        ret = None
        logger.error('In get_village_coordinates: move_to_overview() failed')
    return ret
