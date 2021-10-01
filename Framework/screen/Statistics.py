from Framework.screen.HomeUI import move_to_statistics, move_to_overview
from Framework.utility.Constants import get_XPATH, get_projectLogger
from Framework.utility.SeleniumWebScraper import SWS, Attr


# Project constants
logger = get_projectLogger()
XPATH = get_XPATH()


def get_rank(sws: SWS):
    """
    Gets the current ranking.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - int representing current positon in top, None if error encountered.
    """
    ret = None
    if move_to_statistics(sws):
        rankText = sws.getElementAttribute(XPATH.MY_RANKING, Attr.TEXT)
        if rankText:
            try:
                ret = int(rankText[:-1])
            except (ValueError, IndexError) as err:
                logger.error(f'In get_rank: Failed to retrieve rank. Error: {err}')
        else:
            logger.error('In get_rank: SWS.getElementAttribute() failed')
    else:
        logger.error('In get_rank: move_to_statistics() failed')
    # Return to Overview
    if move_to_overview(sws) and ret:
        logger.success('In get_rank: Rank was successfully retrieved')
    else:
        ret = None
        logger.error('In get_tribe: move_to_overview() failed')
    return ret
