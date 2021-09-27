import pytest
import sys
import os

# Path to root
sys.path.append(os.path.join(sys.path[0], '../'))

from Framework.account.AccountLibraryManager import get_account_library, reset_server_accounts, append_account, \
    get_account_password, get_last_account_username, get_last_account_password, get_generic_accounts, \
    write_account_library
from Framework.account.CreateAccount import create_new_account
from Framework.account.Login import login
from Framework.missions.missions import MissionNum, get_mission_number, open_mission_dialog
from Framework.utility.Constants import Server


class Test_01_account_smokeTest:
    def test_01_account_smokeTest_01(self):
        """
        Id: 01
        Description: Test if accounts from a server may be cleared in `account_library.json`.
        Steps:
            1. Make a backup for `account_library.json`.
            2. Call reset_server_accounts() for each server.
            3. Restore `account_library.json` to initial version.
        Objectives:
            2. Afer each server, the `account_library.json` should contain no accounts for that server.
        """
        # S1. Make a backup for `account_library.json`.
        accLibData = get_account_library()
        assert accLibData is not None

        # S2. Call reset_server_accounts() for each server.
        # O2. Afer each server, the `account_library.json` should contain no accounts for that server.
        for sv in Server:
            assert reset_server_accounts(sv)
            tmpAccLibData = get_account_library()
            assert tmpAccLibData is not None and tmpAccLibData[sv.value] == []

        # S3. Restore `account_library.json` to initial version.
        assert write_account_library(accLibData)

    def test_01_account_smokeTest_02(self):
        """
        Id: 02
        Description: Test if the changes to `account_library.json` are tracked.
        Steps:
            1. Make a backup for `account_library.json`.
            2. Call append_account() with custom strings for each server.
            3. Call get_last_account_username() and get_last_account_password() for each server.
            4. Restore `account_library.json` to initial version.
        Objectives:
            3. Values should correspond to the ones inserted at 2.
        """
        CUSTOM_USERNAME = 'bombardiName'
        CUSTOM_PASSWORD = 'bombardiPassword'
        # S1. Make a backup for `account_library.json`.
        accLibData = get_account_library()
        assert accLibData is not None

        # S2. Call append_account().
        for sv in Server:
            assert append_account(sv, CUSTOM_USERNAME, CUSTOM_PASSWORD)

        # S3. Call get_last_account_username() and get_last_account_password() for each server.
        # O3. Values should correspond to the ones inserted at 2.
        for sv in Server:
            assert get_last_account_username(sv) == CUSTOM_USERNAME
            assert get_last_account_password(sv) == CUSTOM_PASSWORD

        # S4. Restore `account_library.json` to initial version.
        assert write_account_library(accLibData)

    def test_01_account_smokeTest_03(self):
        """
        Id: 03
        Description: Test generic account retrieval.
        Steps:
            1. Make a backup for `account_library.json`.
            2. Add 3 accounts starting with a generic phrase to each server.
            3. Call get_generic_accounts() on each server.
            4. Restore `account_library.json` to initial version.
        Objectives:
            3. Each server should contain the 3 accounts.
        """
        # S1. Make a backup for `account_library.json`.
        accLibData = get_account_library()
        assert accLibData is not None

        # S2. Add 3 accounts starting with a generic phrase to each server.
        # Generic accounts
        GEN = 'DocanuMani'
        usernames = passwords = [GEN + str(index) for index in range(3)]
        for sv in Server:
            for user, pwd in zip(usernames, passwords):
                assert append_account(sv, user, pwd)

        # S3. Call get_generic_accounts() on each server.
        # O3. Each server should contain the 3 accounts.
        for sv in Server:
            genericAccounts = get_generic_accounts(sv, GEN)
            assert genericAccounts is not None and all(user in genericAccounts for user in usernames)

        # S4. Restore `account_library.json` to initial version.
        assert write_account_library(accLibData)

    def test_01_account_smokeTest_04(self):
        """
        Id: 04
        Description: Test password retrieval.
        Steps:
            1. Make a backup for `account_library.json`.
            2. Add 3 accounts to each server.
            3. Call get_account_password() for each added account on each server.
            4. Restore `account_library.json` to initial version.
        Objectives:
            3. The results should match with inserted data.
        """
        # S1. Make a backup for `account_library.json`.
        accLibData = get_account_library()
        assert accLibData is not None

        # S2. Add 3 accounts to each server.
        # Generic accounts
        GEN = 'DocanuMani'
        usernames = passwords = [GEN + str(index) for index in range(3)]
        for sv in Server:
            for user, pwd in zip(usernames, passwords):
                assert append_account(sv, user, pwd)

        # S3. Call get_account_password() for each added account on each server.
        # O3. The results should match with inserted data.
        for sv in Server:
            for user, pwd in zip(usernames, passwords):
                assert get_account_password(sv, user) == pwd

        # S4. Restore `account_library.json` to initial version.
        assert write_account_library(accLibData)

    def test_01_account_smokeTest_05(self):
        """
        Id: 05
        Description: Test account creation and login.
        Steps:
            1. Call create_new_account() with doTasks=True.
            2. Login using get_last_account_username() and get_last_account_password() and open missions dialog.
            3. Call create_new_account() with doTasks=False.
            4. Login using only get_last_account_username() and open missions dialog.
        Objectives:
            2. The mission number should be 1.
            4. The mission popup should have no number.
        """
        sv = Server.S10k
        # S1. Call create_new_account() with doTasks=True.
        assert create_new_account(server=sv, doTasks=True)

        # S2. Login using get_last_account_username() and get_last_account_password() and open missions dialog.
        # O2. The mission number should be 1.
        with login(sv, get_last_account_username(sv), get_last_account_password(sv), headless=True) as sws:
            assert sws is not None
            assert open_mission_dialog(sws)
            assert get_mission_number(sws) == MissionNum.M1

        # S3. Call create_new_account() with doTasks=False.
        assert create_new_account(server=sv, doTasks=False)

        # S4. Login using only get_last_account_username() and open missions dialog.
        # O4. The mission popup should have no number.
        with login(sv, get_last_account_username(sv), headless=True) as sws:
            assert sws is not None
            assert open_mission_dialog(sws)
            assert get_mission_number(sws) == None
