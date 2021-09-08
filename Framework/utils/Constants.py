import os
import json
from enum import IntEnum, Enum
from pathlib import Path

#
# PATHS
#
# Current project
FRAMEWORK_PATH = Path(os.path.dirname(os.path.abspath(__file__))).parent.absolute()
# Chrome driver path
CHROME_DRIVER_PATH = os.path.join(FRAMEWORK_PATH, 'files\chromedriver.exe')
# Data file path
DATA_PATH = os.path.join(FRAMEWORK_PATH, 'files\\data.json')
# Account library file path
ACCOUNT_LIBRARY_PATH = os.path.join(FRAMEWORK_PATH, 'files\\account_library.json')
# Current account file path
ACCOUNT_PATH = os.path.join(FRAMEWORK_PATH, 'files\\account.json')
# Log file path
LOGS_PATH = os.path.join(FRAMEWORK_PATH, 'files\\execution.log')


def get_building_type_by_name(text : str):
    """
    Finds BuildingType based on text.
    Parameters:
        - text (str): Building name to search by.
    Returns:
        - BuildingType.
    """
    text = ''.join([word.capitalize() for word in text.split()])
    for bdType in BuildingType:
        if bdType.name == text:
            return bdType
    print(f'Nothing for {text}')
    return None


class Account:
    def __init__(self):
        try:
            with open(ACCOUNT_PATH, 'r') as f:
                jsonData = f.read()
        except IOError:
            print(f'Please ensure that file {ACCOUNT_PATH} exists and contains the right data')
        self.URL = json.loads(jsonData)['url']
        self.NAME = json.loads(jsonData)['username']
        self.PASS = json.loads(jsonData)['password']
        for tribe in Tribe:
            if tribe.name == str(json.loads(jsonData)['tribe']).upper():
                self.TRIBE = tribe
                break


class Server(Enum):
    NONSTOP = 'https://nonstop.zravian.com/'
    S1 = 'https://s1.zravian.com/'
    S5 = 'https://s5.zravian.com/'
    S10k = 'https://10k.zravian.com/'


# Class to store all XPATH constants
class XPATHCollection(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self):
        super().__init__()
        self.objects = {
            #
            # Temporary email
            #
            'TE_DISABLED_EMAIL_BOX': '//*[@id="mail"][contains(@class, "disabledText")]',
            'TE_COPY_MAIL_BTN': '//*[contains(@class, "copyIconGreenBtn")]',
            'TE_EMAIL_BOX': '//*[contains(@class, "field--value")]',
            'TE_REMOVE_BTN': '//*[contains(@class, "button--remove")]',
            'TE_ZRAVIAN_MAIL': '//*[contains(@class, "inbox__content")]//*[contains(text(), "Welcome to Zravian!")]',
            #
            # Create account
            #
            'STRING_ON_SCREEN': '//*[contains(text(), "%s")]',
            'REGISTER_USER_INPUT': '//*[@id="name"]',
            'REGISTER_PASS1_INPUT': '//*[@id="pw1"]',
            'REGISTER_PASS2_INPUT': '//*[@id="pw2"]',
            'REGISTER_MAIL_INPUT': '//*[@id="mail"]',
            'REGISTER_MAIL2_INPUT': '//*[@id="mail2"]',
            'REGISTER_AGREE_1_CHKBOX': '//*[@id="chk"]',
            'REGISTER_AGREE_2_CHKBOX': '//*[@id="spon"]',
            'REGISTER_SUBMIT_BTN': '//input[@type="submit"][@value="Continue"]',
            'ZRAVIAN_SUCCESS_STATUS': '//legend[contains(text(), "Success")]',
            'ZRAVIAN_ERROR_STATUS': '//legend[contains(text(), "Error")]',
            'ZRAVIAN_ERROR_STATUS_MSG': '//legend[contains(text(), "Error")]/../div',
            #
            # Login
            #
            'LOGIN_USER_INPUT': '//*[@id="name"]',
            'LOGIN_PASS_INPUT': '//*[@id="pass"]',
            'LOGIN_SUBMIT_BTN': '//input[@type="submit"][@value="Log in"]',
            #
            # Profile
            #
            'PROFILE_TRIBE': '//*[@class="details"]//*[contains(text(), "Tribe:")]/..',
            #
            # Screens
            #
            'ROMAN_TASK_MASTER': '//*[@class="ql1"]',
            'TEUTON_TASK_MASTER': '//*[@class="ql2"]',
            'GAUL_TASK_MASTER': '//*[@class="ql3"]',
            'LEVEL_UP_CONE': '//*[@id="cone"]',
            'FINISH_DIALOG': '//*[contains(text(), "Finished in")]',
            'INSIDE_TIMER': './/*[contains(@id, "timer")]',
            #
            # Buildings
            #
            # Production
            'PRODUCTION_LUMBER': '//*[@id="l4"]',
            'PRODUCTION_CLAY': '//*[@id="l3"]',
            'PRODUCTION_IRON': '//*[@id="l2"]',
            'PRODUCTION_CROP': '//*[@id="l1"]',
            'LEVEL_UP_VALUES': '//*[@id="build_value"]',
            # Localization
            'BUILDING_SITE_NAME': '//area[contains(@alt, "%s")]',
            'BUILDING_SITE_ID': '//area[contains(@href, "id=%d")]',
            'BUILDING_PAGE_TITLE': '//*[contains(text(), "%s")]',
            'BUILDING_PAGE_EMPTY_TITLE': '//*[contains(text(), "Construct building.")]',
            # Construct new building menu
            'CONSTRUCT_BUILDING_NAME': '//*[contains(@alt, "%s")]/../../../..',
            'CONSTRUCT_BUILDING_BTN': './/*[contains(text(), "Construct buildings")]',
            # Constructing/Leveling up errors
            'BUILDING_ERR_RESOURCES': './/*[contains(text(), "Enough resources in")]',
            'BUILDING_ERR_WH': './/*[contains(text(), "Upgrade your warehouse")]',
            'BUILDING_ERR_GR': './/*[contains(text(), "Upgrade your granary")]',
            'BUILDING_ERR_BUSY_WORKERS': './/*[contains(text(), "Your builders are already working")]',
            'BUILDING_ERR_MAX_LVL': '//*[contains(text(), "fully upgraded")]',
            # Costs
            'LEVEL_UP_COSTS': '//*[@id="contract"]',
            'CONSTRUCT_COSTS': './/*[@class="res"]',
            # SUCCESSFUL UPGRADE
            'CONSTRUCT_BUILDING_ID': './/*[contains(text(), "Construct buildings")]',
            'LEVEL_UP_BUILDING_BTN': '//*[contains(text(), "Upgrade to level")]',
            # DEMOLITION
            'DEMOLITION_BUILDING_OPTION': '//*[contains(text(), "%s")]',
            'DEMOLITION_BTN': '//*[@id="btn_demolish"]',
            #
            # Academy
            #
            'RESEARCH_TROOP': '//*[contains(text(), "%s")]/../../..//*[contains(text(), "Research")]',
            # Research errors
            'RESEARCH_ERR_RESOURCES': '//*[contains(text(), "%s")]/../../..//*[contains(text(), "Not enough resources")]',
        }
        for key, value in self.objects.items():
            self.__setitem__(key, value)


# Enum of all existing tribes
class Tribe(Enum):
    ROMANS = 'ROMANS'
    TEUTONS = 'TEUTONS'
    GAULS = 'GAULS'
    

# Enum of all existing buildings
class BuildingType(IntEnum):
    EmptyPlace = 0
    Woodcutter = 1
    ClayPit = 2
    IronMine = 3
    Cropland = 4
    Sawmill = 5
    Brickworks = 6
    IronFoundry = 7
    FlourMill = 8
    Bakery = 9
    Warehouse = 10
    Granary = 11
    Blacksmith = 12
    Armoury = 13
    TournamentSquare = 14
    MainBuilding = 15
    RallyPoint = 16
    Marketplace = 17
    Embassy = 18
    Barracks = 19
    Stable = 20
    SiegeWorkshop = 21
    Academy = 22
    Cranny = 23
    TownHall = 24
    Residence = 25
    Palace = 26
    TradeOffice = 28
    GreatBarracks = 29
    GreatStable = 30
    Wall = 32
    Stonemason = 34
    Brewery = 35
    Trapper = 36
    HeroMansion = 37
    GreatWarehouse = 38
    GreatGranary = 39


# Enum of all existing units
class TroopType(Enum):
    Legionnaire = 1
    Praetorian = 2
    Imperian = 3
    Equites_Legati = 4
    Equites_Imperatoris = 5
    Equites_Caesaris = 6
    RRam = 7
    Fire_Catapult = 8
    Senator = 9
    RSettler = 10
    Clubswinger = 11
    Spearman = 12
    Axeman = 13
    Scout = 14
    Paladin = 15
    Teutonic_Knight = 16
    TRam = 17
    Catapult = 18
    Chieftain = 19
    TSettler = 20
    Phalanx = 21
    Swordsman = 22
    Pathfinder = 23
    Theutates_Thunder = 24
    Druidrider = 25
    Haeduan = 26
    Battering_Ram = 27
    Trebuchet = 28
    Chief = 29
    GSettler = 30


# Class containing building properties
class Building:
    def __init__(self, data):
        self.id = data['id']
        self.type = BuildingType(self.id)
        self.name = data['name']
        self.requirements = []
        for building, level in data['requirements']:
            self.requirements.append((get_building_type_by_name(building), level))


# Class containing troop properties
class Troop:
    def __init__(self, data, type):
        self.type = type
        self.name = data['name']
        self.attack = data['attack']
        self.defenseInfantry = data['defenseInfantry']
        self.defenseCavalry = data['defenseCavalry']
        self.costs = data['costs']
        self.capacity = data['capacity']
        self.upkeep = data['upkeep']
        self.requirements = []
        for building, level in data['requirements']:
            self.requirements.append((get_building_type_by_name(building), level))


# Getters
# Singleton Instances
XPATHCollectionInstance = None
BUILDINGSInstance = None
TROOPSInstance = None
ACCOUNTInstance = None


def init_data():
    """
    Initialises constants by parsing data.json.
    """
    global TROOPSInstance
    global BUILDINGSInstance
    # Init
    BUILDINGSInstance = {}
    TROOPSInstance = {}
    # Read data
    with open(DATA_PATH, 'r') as f:
        jsonData = f.read()
    # Populate buildings
    buildings = json.loads(jsonData)['buildings']
    assert len(buildings) == len(BuildingType)
    for bdType, bdData in zip(BuildingType, buildings):
        assert bdType == bdData['id']
        BUILDINGSInstance[bdType] = Building(bdData)
    # Populate troops
    troops = json.loads(jsonData)['troops']['romans']
    troops += json.loads(jsonData)['troops']['teutons']
    troops += json.loads(jsonData)['troops']['gauls']
    assert len(troops) == len(TroopType)
    for troopType, troopData in zip(TroopType, troops):
        troopName = ' '.join(troopType.name.split('_'))
        assert troopName == troopData['name'] or troopName[1:] == troopData['name']
        TROOPSInstance[troopType] = Troop(troopData, troopType)


def get_BUILDINGS():
    """
    Instantiates BUILDINGSInstance if needed.
    
    Returns:
        - Dictionary linking buildingType to Building(object).
    """
    if BUILDINGSInstance is None:
        init_data()
    return BUILDINGSInstance


def get_TROOPS():
    """
    Instantiates TROOPSInstance if needed.
    
    Returns:
        - Dictionary linking buildingType to Troop(object).
    """
    if TROOPSInstance is None:
        init_data()
    return TROOPSInstance


def get_XPATH():
    """
    Instantiate XPATHCollectionInstance if needed.
    
    Returns:
        - Object containing all XPATH constants used.
    """
    global XPATHCollectionInstance
    if XPATHCollectionInstance is None:
        XPATHCollectionInstance = XPATHCollection()
    return XPATHCollectionInstance


def get_ACCOUNT():
    """
    Instantiates TROOPSInstance if needed.
    
    Returns:
        - Object containing account data extracted from account.json.
    """
    global ACCOUNTInstance
    if ACCOUNTInstance is None:
        ACCOUNTInstance = Account()
    return ACCOUNTInstance
