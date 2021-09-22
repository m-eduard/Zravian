from Framework.utility.Constants import get_XPATH
from Framework.utility.Logger import get_projectLogger
from Framework.utility.SeleniumUtils import SWS
from Framework.screen.Views import Views, get_current_view


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
    rank = None
    if get_current_view(sws) == Views.STATS:
        rank = sws.getElementAttribute(XPATH.MY_RANKING, 'text')
        if rank:
            try:
                rank = int(rank[:-1])
            except ValueError as e:
                logger.error(f'In get_rank: Failed to convert rank to int. Error: {e}')
            except IndexError as e:
                logger.error(f'In get_rank: Rank text is empty. Error: {e}')
        else:
            logger.error('In get_rank: Failed to get current rank')
    else:
        logger.error('In get_rank: View is not statistics')
    return rank

