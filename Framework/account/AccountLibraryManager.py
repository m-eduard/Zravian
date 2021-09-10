import json
from Framework.utility.Logger import get_projectLogger
from Framework.utility.Constants import ACCOUNT_LIBRARY_PATH, Server

# Constants
logger = get_projectLogger()
# JSON username key
JSON_USERNAME_KEY = "username"
# JSON password key
JSON_PASSWORD_KEY = "password"


def get_account_library():
    """
    Gets data contained in `account_library.json` in json format.

    Returns:
        - Dictionary containing json if operation was successful, None otherwise.
    """
    ret = None
    jsonData = None
    try:
        with open(ACCOUNT_LIBRARY_PATH, 'r') as f:
            jsonData = f.read()
    except IOError:
        logger.error(f'Please ensure that file {ACCOUNT_LIBRARY_PATH} exists and contains the right data')
    decodedJson = None
    if jsonData:
        try:
            decodedJson = json.loads(jsonData)
        except json.JSONDecodeError:
            logger.error(f'Invalid json format in file {ACCOUNT_LIBRARY_PATH}')
    if decodedJson:
        for sv in Server:
            if not sv.value in decodedJson or \
                    not isinstance(decodedJson[sv.value], list) or \
                    not all(isinstance(elem, dict) for elem in decodedJson[sv.value]) or \
                    not (JSON_USERNAME_KEY in elem and JSON_PASSWORD_KEY in elem for elem in decodedJson[sv.value]):
                logger.error('In get_account_library: JSON does not have the proper form')
                break
        else:
            ret = decodedJson
    return ret


def write_account_library(newData : dict):
    """
    Overwrites data in `account_library.json`.

    Parameters:
        - newData (Dictionary): Will update json with it.

    Returns:
        - True if the operation was successful, False otherwise.
    """
    ret = False
    try:
        with open(ACCOUNT_LIBRARY_PATH, 'w') as f:
            f.write(json.dumps(newData, indent=4, sort_keys=False))
            ret = True
    except IOError:
        logger.error(f'Please ensure that file {ACCOUNT_LIBRARY_PATH} exists and contains the right data')
    return ret


def reset_server_accounts(server : Server):
    """
    Resets all accounts from one server:

    Parameters:
        - server (Server): Denotes server.

    Returns:
        - True if operation was successful, None otherwise.
    """
    ret = None
    initialJson = get_account_library()
    if initialJson:
        initialJson[server.value] = {}
        if write_account_library(initialJson):
            ret = True
        else:
            logger.error('IN reset_server_accounts: Failed to write to `account_library.json`')
    else:
        logger.error('IN reset_server_accounts: Failed to get `account_library.json`')
    return ret


def append_account(newAccount : dict, server : Server):
    """
    Appends a new account to `account_library.json`.

    Parameters:
        - newAccount (dict): Contains new account data.
        - server (Server): Denotes server. 

    Returns:
        - True if the operation was successful, False otherwise.
    """
    ret = False
    decodedJson = get_account_library()
    if decodedJson:
        for acc in decodedJson[server.value]:
            if acc[JSON_USERNAME_KEY] == newAccount[JSON_USERNAME_KEY]:
                logger.warning('In append_account: Account already exists')
                ret = True
                break
        else:
            decodedJson[server.value].append(newAccount)
            if write_account_library(decodedJson):
                ret = True
            else:
                logger.error('In append_account: Failed to write to account_library.json')
    else:
        logger.error('In append_account: Failed to read account_library.json')
    return ret


def get_account(username : str, server : Server):
    """
    Gets account from `account_library.json` if it exists.

    Parameters:
        - username (String): Identifies the account.
        - server (Server): Identifies the server.

    Returns:
        - Dictionary containing account if it exists, None otherwise.
    """
    ret = None
    decodedJson = get_account_library()
    if decodedJson:
        for acc in decodedJson[server.value]:
            if acc[JSON_USERNAME_KEY] == username:
                ret = acc
                break
        else:
            logger.warning(f'In get_account: Failed to retrieve {username} on {server.value}')
    else:
        logger.error('In get_account: Failed to read `account_library.json`')
    return ret


def get_last_account(server : Server):
    """
    Gets most recent account from `account_library.json` if it exists.

    Parameters:
        - username (String): Identifies the account.
        - server (Server): Identifies the server.

    Returns:
        - Dictionary containing account if it exists, None otherwise.
    """
    ret = None
    decodedJson = get_account_library()
    if decodedJson:
        if decodedJson[server.value]:
            ret = decodedJson[server.value][-1]
        else:
            logger.warning(f'In get_random_account: No accounts on server')
    else:
        logger.error('In get_random_account: Failed to read `account_library.json`')
    return ret
