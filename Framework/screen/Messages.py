from Framework.screen.HomeUI import move_to_messages, move_to_overview
from Framework.utility.Constants import get_XPATH, get_projectLogger
from Framework.utility.SeleniumWebScraper import SWS


# Project constants
logger = get_projectLogger()
XPATH = get_XPATH()


def read_all_new_messages(sws: SWS):
    """
    Reads all new messages, does not store them.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - True if operation was successful, False otherwise.
    """
    ret = False
    NEW_MSG_TEXT = '(new)'
    if move_to_messages(sws):
        while sws.isVisible(XPATH.STRING_ON_SCREEN % NEW_MSG_TEXT):
            if sws.clickElement(f"{XPATH.STRING_ON_SCREEN % NEW_MSG_TEXT}/*", refresh=True):
                if not move_to_messages(sws, forced=True):
                    logger.error('In read_all_new_messages: move_to_messages() failed')
                    break
            else:
                logger.error('In read_all_new_messages: sws.ClickElement() failed')
                break
        else:
            ret = True
    else:
        logger.error('In read_all_new_messages: move_to_messages() failed')
    # Return to Overview
    if move_to_overview(sws) and ret:
        logger.success('In read_all_new_messages: All new messages were read')
    else:
        ret = False
        logger.error('In read_all_new_messages: move_to_overview() failed')
    return ret