# Account directory description

**Module AccountLibraryManager** should be used for any interaction with
account database stored in `account_library.json`. It provides the interface
to access data and update it and ensures data will not be corrupt.
<br><br>


**Module Login** contains function `login()` which is the entry point for every
framework interaction with the game, except the account creation which is a
stand-alone process.
<br><br>


**Module CreateAccount** contains the necessary tools to create a new account
and provides the interface to do so with function `create_new_account()`,
allowing genericity and accessibility for development stages.
<br><br>
