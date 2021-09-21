from Framework.utility.Constants import get_XPATH
from Framework.utility.Logger import get_projectLogger
from Framework.utility.SeleniumUtils import SWS
from Framework.screen.Views import Views, get_current_view, move_to_reports


# Project constants
logger = get_projectLogger()
XPATH = get_XPATH()


def read_all_new_reports(sws : SWS):
    """
    Reads all new reports, does not store them.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - True if operation was successful, False otherwise.
    """
    ret = False
    UNREAD_REPORT_TEXT = '(unread)'
    if get_current_view(sws) == Views.REPORTS:
        while sws.isVisible(XPATH.STRING_ON_SCREEN % UNREAD_REPORT_TEXT):
            if sws.clickElement(f"{XPATH.STRING_ON_SCREEN % UNREAD_REPORT_TEXT}/*", refresh=True):
                if not move_to_reports(sws, forced=True):
                    logger.error('In read_all_new_reports: Failed to return to reports')
                    break
            else:
                logger.error('In read_all_new_reports: Failed to open new message')
                break
        else:
            ret = True
    else:
        logger.error('In get_rank: View is not reports')
    return ret
