import json
from Framework.utility.Logger import get_projectLogger
from Framework.utility.Constants import ACCOUNT_LIBRARY_PATH, Server

# Constants
logger = get_projectLogger()
# JSON username key
JSON_USERNAME_KEY = "username"
# JSON password key
JSON_PASSWORD_KEY = "password"


def __get_account_library():
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
                logger.error('In __get_account_library: JSON does not have the proper form')
                break
        else:
            ret = decodedJson
    return ret


def __write_account_library(newData : dict):
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
    initialJson = __get_account_library()
    if initialJson:
        initialJson[server.value] = {}
        if __write_account_library(initialJson):
            ret = True
        else:
            logger.error('IN reset_server_accounts: Failed to write to `account_library.json`')
    else:
        logger.error('IN reset_server_accounts: Failed to get `account_library.json`')
    return ret


def append_account(server : Server, username : str, password : str):
    """
    Appends a new account to `account_library.json`.

    Parameters:
        - server (Server): Denotes server. 
        - username (String): Identifies the account.
        - password (String): Account password.

    Returns:
        - True if the operation was successful, False otherwise.
    """
    ret = False
    decodedJson = __get_account_library()
    if decodedJson:
        for acc in decodedJson[server.value]:
            if acc[JSON_USERNAME_KEY] == username:
                logger.warning(f'In append_account: Account already exists {username}')
                ret = True
                break
        else:
            newAccount = {
                JSON_USERNAME_KEY: username,
                JSON_PASSWORD_KEY: password,
            }
            decodedJson[server.value].append(newAccount)
            if __write_account_library(decodedJson):
                ret = True
            else:
                logger.error('In append_account: Failed to write to account_library.json')
    else:
        logger.error('In append_account: Failed to read account_library.json')
    return ret


def get_account_password(server : Server, username : str):
    """
    Gets account password from `account_library.json` if the username exists.

    Parameters:
        - server (Server): Identifies the server.
        - username (String): Identifies the account.

    Returns:
        - Dictionary containing account if it exists, None otherwise.
    """
    ret = None
    decodedJson = __get_account_library()
    if decodedJson:
        for acc in decodedJson[server.value]:
            if acc[JSON_USERNAME_KEY] == username:
                ret = str(acc[JSON_PASSWORD_KEY])
                break
        else:
            logger.warning(f'In get_account: Failed to retrieve {username} on {server.value}')
    else:
        logger.error('In get_account: Failed to read `account_library.json`')
    return ret


def get_last_account_username(server : Server):
    """
    Gets most recent account username from `account_library.json` if file is not empty.

    Parameters:
        - server (Server): Identifies the server.

    Returns:
        - String with password if operation was successful, None otherwise.
    """
    ret = None
    decodedJson = __get_account_library()
    if decodedJson:
        if decodedJson[server.value]:
            ret = str(decodedJson[server.value][-1][JSON_USERNAME_KEY])
        else:
            logger.warning(f'In get_last_account_username: No accounts on server')
    else:
        logger.error('In get_last_account_username: Failed to read `account_library.json`')
    return ret


def get_last_account_password(server : Server):
    """
    Gets most recent account password from `account_library.json` if file is not empty.

    Parameters:
        - server (Server): Identifies the server.

    Returns:
        - String with password if operation was successful, None otherwise.
    """
    ret = None
    decodedJson = __get_account_library()
    if decodedJson:
        if decodedJson[server.value]:
            ret = str(decodedJson[server.value][-1][JSON_PASSWORD_KEY])
        else:
            logger.warning(f'In get_last_account_password: No accounts on server')
    else:
        logger.error('In get_last_account_password: Failed to read `account_library.json`')
    return ret


def get_generic_accounts(server : Server, genericPhrase : str):
    """
    Gets all generic accounts created with the given genericPhrase.

    Parameters:
        - genericPhrase (str): Phrase to search for in accounts username.
        - server (Server): Identifies the server.

    Returns:
        - List containing all generic accounts, None if error is encountered.
    """
    ret = None
    decodedJson = __get_account_library()
    if decodedJson:
        ret = [str(acc[JSON_USERNAME_KEY]) for acc in decodedJson[server.value] \
                if str(acc[JSON_USERNAME_KEY]).startswith(genericPhrase)]
    else:
        logger.error('In append_account: Failed to read account_library.json')
    return ret
