import re
from Framework.screen.Navigation import move_to_overview
from Framework.screen.OVillage import get_village_name
from Framework.screen.Profile import get_capital
from Framework.utility.Constants import Server, get_XPATH, get_projectLogger
from Framework.utility.SeleniumWebScraper import SWS


# Project constants
logger = get_projectLogger()
XPATH = get_XPATH()


def get_server(sws: SWS):
    """
    Gets the current server.

    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - Current server if operation is successful, None otherwise.
    """
    ret = None
    serverURL = None
    try:
        serverURL = re.match(r'(.*)\/(.*)', sws.getCurrentUrl()).group(1) + '/'
    except AttributeError as err:
        logger.error(f'In get_server: Regex failed to extract server: {err}')
    if serverURL:
        for server in Server:
            if server.value == serverURL:
                ret = server
                break
        else:
            logger.error(f'In get_server: Unknown server {serverURL}')
    return ret


def in_capital(sws: SWS):
    """
    Checks if the current village is capital.
    
    Parameters:
        - sws (SWS): Selenium Web Scraper.

    Returns:
        - True if current village is capital, False otherwise.
    """
    ret = False
    capital = get_capital(sws)
    if capital:
        villageName = get_village_name(sws)
        if villageName:
            if capital == villageName:
                ret = True
            else:
                logger.info('In in_capital: Currently not in capital')
        else:
            logger.error('In in_capital: get_village_name() failed')
    else:
        logger.error('In in_capital: get_capital() failed')
    return ret


def return_stable(func):
    """
    Will run func and attempt to return to overview.

    Parameters:
        - func (Function): Function to call.
    """
    def wrapper(*args, **kwargs):
        sws = None
        for arg in args:
            if isinstance(arg, SWS):
                sws = arg
                break
        else:
            logger.err(f'In return_stable: Failed to get SWS from {func}`s args')
        if sws:
            ret = func(*args, **kwargs)
            if not move_to_overview(sws):
                if isinstance(ret, bool):
                    ret = False
                else:
                    ret = None
                logger.error(f'In {func}: move_to_overview failed')
        return ret
    return wrapper
