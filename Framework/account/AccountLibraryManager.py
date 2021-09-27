import json
from Framework.utility.Constants import ACCOUNT_LIBRARY_PATH, Server, get_projectLogger


# Project constants
logger = get_projectLogger()
# JSON username key
JSON_USERNAME_KEY = "username"
# JSON password key
JSON_PASSWORD_KEY = "password"


def check_account_library_format(accountLib : dict):
    """
    Checks whether a given dictionary respects the account_library.json pattern.

    Parameters:
        - accountLib (Dictionary): Will update json with it.

    Returns:
        - True if the operation was successful, False otherwise.
    """
    ret = False
    for sv in Server:
        if sv.value in accountLib and \
                (isinstance(accountLib[sv.value], list) or accountLib[sv.value] == {}) and \
                all(isinstance(elem, dict) for elem in accountLib[sv.value]) and \
                (JSON_USERNAME_KEY in elem and JSON_PASSWORD_KEY in elem for elem in accountLib[sv.value]):
            continue
        logger.error('In check_account_library_format: JSON does not have the proper form')
        break
    else:
        ret = True
    return ret


def get_account_library():
    """
    Gets data contained in `account_library.json` as dictionary if it has no format errors.

    Returns:
        - Dictionary containing json if operation was successful, None otherwise.
    """
    ret = None
    jsonData = None
    try:
        with open(ACCOUNT_LIBRARY_PATH, 'r') as f:
            jsonData = f.read()
    except IOError:
        logger.error(f'In get_account_library: Failed to open {ACCOUNT_LIBRARY_PATH}')
    accountLib = None
    if jsonData:
        try:
            accountLib = dict(json.loads(jsonData))
        except (json.JSONDecodeError, ValueError):
            logger.error(f'In get_account_library: Invalid json format in file {ACCOUNT_LIBRARY_PATH}')
    if accountLib and check_account_library_format(accountLib):
        ret = accountLib
    else:
        logger.error('In get_account_library: JSON failed format check')
    return ret


def write_account_library(newAccountLib : dict):
    """
    Overwrites data in `account_library.json`.

    Parameters:
        - newAccountLib (Dictionary): Will update json with it.

    Returns:
        - True if the operation was successful, False otherwise.
    """
    ret = False
    if check_account_library_format(newAccountLib):
        try:
            with open(ACCOUNT_LIBRARY_PATH, 'w') as f:
                f.write(json.dumps(newAccountLib, indent=4, sort_keys=False))
                ret = True
        except IOError:
            logger.error(f'In write_account_library: Failed to open {ACCOUNT_LIBRARY_PATH}')
    else:
        logger.error('In write_account_library: JSON failed format check')
    return ret


def reset_server_accounts(server : Server):
    """
    Resets all accounts from one server:

    Parameters:
        - server (Server): Denotes server.

    Returns:
        - True if operation was successful, False otherwise.
    """
    ret = False
    accountLib = get_account_library()
    if accountLib:
        accountLib[server.value] = []
        if write_account_library(accountLib):
            ret = True
        else:
            logger.error('In reset_server_accounts: Failed to write to `account_library.json`')
    else:
        logger.error('In reset_server_accounts: Failed to get `account_library.json`')
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
    decodedJson = get_account_library()
    if decodedJson:
        for acc in decodedJson[server.value]:
            if acc[JSON_USERNAME_KEY] == username:
                ret = str(acc[JSON_PASSWORD_KEY])
                break
        else:
            logger.info(f'In get_account_password: Failed to retrieve {username} on {server.value}')
    else:
        logger.error('In get_account_password: Failed to read `account_library.json`')
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
    accountLib = get_account_library()
    if accountLib:
        if get_account_password(server, username):
            logger.warning(f'In append_account: Account already exists {username}')
            ret = True
        else:
            newAccount = {
                JSON_USERNAME_KEY: username,
                JSON_PASSWORD_KEY: password,
            }
            accountLib[server.value].append(newAccount)
            if write_account_library(accountLib):
                logger.info(f'In append_account: Added account {username}: {password}')
                ret = True
            else:
                logger.error('In append_account: Failed to write to account_library.json')
    else:
        logger.error('In append_account: Failed to read account_library.json')
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
    accountLib = get_account_library()
    if accountLib:
        if accountLib[server.value]:
            try:
                ret = str(accountLib[server.value][-1][JSON_USERNAME_KEY])
            except IndexError:
                logger.error(f'In get_last_account_username: {server.value} is empty')
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
    accountLib = get_account_library()
    if accountLib:
        try:
            ret = str(accountLib[server.value][-1][JSON_PASSWORD_KEY])
        except IndexError:
            logger.error(f'In get_last_account_password: {server.value} is empty')
    else:
        logger.error('In get_last_account_password: Failed to read `account_library.json`')
    return ret


def get_generic_accounts(server : Server, genericPhrase : str):
    """
    Gets all generic accounts created with the given genericPhrase.

    Parameters:
        - server (Server): Identifies the server.
        - genericPhrase (str): Phrase to search for in accounts username.

    Returns:
        - List containing all generic accounts, None if error is encountered.
    """
    ret = None
    accountLib = get_account_library()
    if accountLib:
        ret = [str(acc[JSON_USERNAME_KEY]) for acc in accountLib[server.value] \
                if str(acc[JSON_USERNAME_KEY]).startswith(genericPhrase)]
    else:
        logger.error('In get_generic_accounts: Failed to read account_library.json')
    return ret
