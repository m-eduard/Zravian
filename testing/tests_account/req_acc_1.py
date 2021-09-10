import unittest
import json
from Framework.utility.Constants import ACCOUNT_LIBRARY_PATH, Server
from Framework.utility.Logger import get_projectLogger
from Framework.account.CreateAcoount import create_new_account

# Constants
logger = get_projectLogger()


class Test_AccountCreation(unittest.TestCase):
    def setUp(self):
        logger.set_debugMode(True)

    def test_create_account(self):
        # Step 1: Read account_library.json before account creation
        # Step 1.1: Read json from file
        jsonData = None
        try:
            with open(ACCOUNT_LIBRARY_PATH, 'r') as f:
                jsonData = f.read()
        except IOError:
            logger.error(f'Please ensure that file {ACCOUNT_LIBRARY_PATH} exists and contains the right data')
        self.assertIsNotNone(jsonData)
        # Step 1.2: Create json object
        initialJson = None
        try:
            initialJson = json.loads(jsonData)
        except json.JSONDecodeError:
            logger.error(f'Invalid json format in file {ACCOUNT_LIBRARY_PATH}')
        self.assertIsNotNone(initialJson)
        # Step 2: Create an account on each server
        for sv in Server:
            self.assertTrue(create_new_account(server=sv))
        # Step 3: Read account_library.json after account creation
        # Step 3.1: Read json from file
        jsonData = None
        try:
            with open(ACCOUNT_LIBRARY_PATH, 'r') as f:
                jsonData = f.read()
        except IOError:
            logger.error(f'Please ensure that file {ACCOUNT_LIBRARY_PATH} exists and contains the right data')
        self.assertIsNotNone(jsonData)
        # Step 3.2: Create json object
        currentJson = None
        try:
            currentJson = json.loads(jsonData)
        except json.JSONDecodeError:
            logger.error(f'Invalid json format in file {ACCOUNT_LIBRARY_PATH}')
        self.assertIsNotNone(currentJson)
        # Step 4: Check differences
        for sv in Server:
            self.assertTrue(len(currentJson[str(sv.value)]) == len(initialJson[str(sv.value)]) + 1)
        

if __name__ == '__main__':
    unittest.main()
