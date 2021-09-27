from Framework.screen.HomeUI import move_to_reports, move_to_overview
from Framework.utility.Constants import get_XPATH, get_projectLogger
from Framework.utility.SeleniumWebScraper import SWS


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
    if move_to_reports(sws):
        while sws.isVisible(XPATH.STRING_ON_SCREEN % UNREAD_REPORT_TEXT):
            if sws.clickElement(f"{XPATH.STRING_ON_SCREEN % UNREAD_REPORT_TEXT}/*", refresh=True):
                if not move_to_reports(sws, forced=True):
                    logger.error('In read_all_new_reports: Failed to return to Reports')
                    break
            else:
                logger.error('In read_all_new_reports: Failed to open new report')
                break
        else:
            ret = True
    else:
        logger.error('In read_all_new_reports: Failed to move to Reports')
    # Return to Overview
    if move_to_overview(sws) and ret:
        logger.success('In read_all_new_reports: All new reports were read')
    else:
        ret = False
        logger.error('In read_all_new_reports: Failed to move to Overview')
    return ret
