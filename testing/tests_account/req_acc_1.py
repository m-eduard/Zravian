import unittest
from Framework.account.AccountLibraryManager import JSON_PASSWORD_KEY, JSON_USERNAME_KEY, get_account_library, get_random_account
from Framework.utility.Constants import Server
from Framework.utility.Logger import get_projectLogger
from Framework.account.CreateAcoount import create_new_account

# Constants
logger = get_projectLogger()


class Test_AccountCreation(unittest.TestCase):
    def setUp(self):
        logger.set_debugMode(True)

    def test_account_library(self):
        self.assertIsNotNone(get_account_library())

    def test_create_account(self):
        initialJson = get_account_library()
        self.assertIsNotNone(initialJson)
        for sv in Server:
            self.assertTrue(create_new_account(server=sv))
        currentJson = get_account_library()
        self.assertIsNotNone(currentJson)
        for sv in Server:
            self.assertTrue(len(currentJson[str(sv.value)]) == len(initialJson[str(sv.value)]) + 1)

    def test_create_account_dup_name(self):
        credentials = None
        for sv in Server:
            credentials = get_random_account(sv)
            if credentials:
                break
        self.assertIsNotNone(credentials)
        self.assertFalse(create_new_account(credentials[JSON_USERNAME_KEY], credentials[JSON_PASSWORD_KEY]))
        

if __name__ == '__main__':
    unittest.main()
