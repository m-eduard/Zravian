from Framework.screen.HomeUI import move_to_reports, move_to_overview
from Framework.utility.Constants import get_XPATH, get_projectLogger
from Framework.utility.SeleniumWebScraper import SWS


# Project constants
logger = get_projectLogger()
XPATH = get_XPATH()


def read_all_new_reports(sws: SWS):
    """
    Reads all new reports, does not store them.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - True if operation was successful, False otherwise.
    """
    ret = False
    UNREAD_REPORT_TEXT = '(unread)'
    if move_to_reports(sws):
        while sws.isVisible(XPATH.STRING_ON_SCREEN % UNREAD_REPORT_TEXT):
            if sws.clickElement(f"{XPATH.STRING_ON_SCREEN % UNREAD_REPORT_TEXT}/*", refresh=True):
                if not move_to_reports(sws, forced=True):
                    logger.error('In read_all_new_reports: move_to_reports() failed')
                    break
            else:
                logger.error('In read_all_new_reports: SWS.clickElement() failed')
                break
        else:
            ret = True
    else:
        logger.error('In read_all_new_reports: move_to_reports() failed')
    # Return to Overview
    if move_to_overview(sws) and ret:
        logger.success('In read_all_new_reports: All new reports were read')
    else:
        ret = False
        logger.error('In read_all_new_reports: move_to_overview() failed')
    return ret
