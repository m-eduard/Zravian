from Framework.screen.HomeUI import move_to_statistics, move_to_overview
from Framework.utility.Constants import get_XPATH
from Framework.utility.Logger import get_projectLogger
from Framework.utility.SeleniumUtils import SWS


# Project constants
logger = get_projectLogger()
XPATH = get_XPATH()


def get_rank(sws : SWS):
    """
    Gets the current ranking.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - int representing current positon in top, None if error encountered.
    """
    ret = None
    if move_to_statistics(sws):
        rankText = sws.getElementAttribute(XPATH.MY_RANKING, 'text')
        if rankText:
            if move_to_overview(sws):
                try:
                    ret = int(rankText[:-1])
                except (ValueError, IndexError) as err:
                    logger.error(f'In get_rank: Failed to retrieve rank. Error: {err}')
            else:
                logger.error('In get_rank: Failed to move to Overview')
        else:
            logger.error('In get_rank: Failed to get current rank')
    else:
        logger.error('In get_rank: Failed to move to Statistics')
    # Return to Overview
    if move_to_overview(sws) and ret:
        logger.success('In get_rank: Rank was successfully retrieved')
    else:
        ret = None
        logger.error('In get_tribe: Failed to move to Overview')
    return ret

