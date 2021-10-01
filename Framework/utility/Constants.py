import os
import json
from enum import IntEnum, Enum
from pathlib import Path
from collections import namedtuple
from Framework.utility.Logger import ProjectLogger


#
# PATHS
#
# Current project
FRAMEWORK_PATH = Path(os.path.dirname(os.path.abspath(__file__))).parent.absolute()
# Chrome driver path
CHROME_DRIVER_PATH = os.path.join(FRAMEWORK_PATH, *('files\\chromedriver.exe'.split('\\')))
# Data file path
DATA_PATH = os.path.join(FRAMEWORK_PATH, *('files\\data.json'.split('\\')))
# Account library file path
ACCOUNT_LIBRARY_PATH = os.path.join(FRAMEWORK_PATH, *('files\\account_library.json'.split('\\')))
# Log file path
LOGS_PATH = os.path.join(FRAMEWORK_PATH, *('files\\execution.log'.split('\\')))


# Project singletons
XPATHCollectionInstance = None
BUILDINGS_DATA_Instance = None
TROOPSInstance = None
# Logger will be initialised to provide features for other elements
logger = ProjectLogger()


# General purpose functions
def time_to_seconds(currTime: str):
    """
    Converts time in format hh:mm:ss to seconds

    Parameters:
        - currTime (str): Time in format hh:mm:ss.

    Returns:
        - Equivalent time in seconds.
    """
    SECONDS_IN_HOUR = 3600
    SECONDS_IN_MIN = 60
    ret = None
    try:
        h, m, s = currTime.split(':')
        ret = int(h) * SECONDS_IN_HOUR + int(m) * SECONDS_IN_MIN + int(s)
    except ValueError as err:
        logger.error(f'In time_to_seconds: Invalid time format: {err}')
    return ret


def get_building_type_by_name(text: str):
    """
    Finds BuildingType based on text.
    Parameters:
        - text (str): Building name to search by.
    Returns:
        - BuildingType.
    """
    ret = None
    text = ''.join([word.capitalize() for word in text.split()])
    for bdType in BuildingType:
        if bdType.name == text:
            ret = bdType
            break
    else:
        logger.error(f'In get_building_type_by_name: Failed to get building type from "{text}"')
    return ret


# Servers list
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
            'TE_RANDOM_BTN': '//input[@type="submit"][@value="Random"]',
            'TE_REFRESH_BTN': '//*[@class="action-item refresh"]',
            'TE_EMAIL_ADDRESS': '//*[@id="current-id"]',
            'TE_ZRAVIAN_MAIL': '//*[@class="subject"][contains(text(), "Welcome to Zravian!")]/..',
            'TE_ZRAVIAN_RECOVERY_MAIL': '//*[@class="subject"][contains(text(), "Zravian password reset")]',
            'TE_EMAIL_TEXT': '//*[contains(@id, "content-%s")]//*[@class="message"]',
            #
            # Create account
            #
            'STRING_ON_SCREEN': '//*[contains(text(), "%s")]',
            'NEW_ACC_USER_INPUT': '//*[@id="name"]',
            'NEW_ACC_PASS1_INPUT': '//*[@id="pw1"]',
            'NEW_ACC_PASS2_INPUT': '//*[@id="pw2"]',
            'NEW_ACC_MAIL_INPUT': '//*[@id="mail"]',
            'NEW_ACC_MAIL2_INPUT': '//*[@id="mail2"]',
            'NEW_ACC_AGREE_1_CHKBOX': '//*[@id="chk"]',
            'NEW_ACC_AGREE_2_CHKBOX': '//*[@id="spon"]',
            'NEW_ACC_SUBMIT_BTN': '//input[@type="submit"][@value="Continue"]',
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
            # General
            #
            'FINISH_DIALOG': '//*[contains(text(), "Finished in")]',
            'INSIDE_TIMER': '//*[contains(@id, "timer")]',
            #
            # Profile
            #
            'EDIT_PROFILE': '//a[text()="Edit profile"]',
            'PROFILE_DESCR': '//*[@id="edit"]//textarea[@name="be2"]',
            'PROFILE_TRIBE': '//*[@class="details"]//*[contains(text(), "Tribe:")]/..',
            'PROFILE_CAPITAL': '//*[@id="villages"]//*[@class="none3"][contains(text(), "(capital)")]/../nam',
            'PROFILE_OK_BTN': '//*[@id="btn_ok"]',
            'SELECT_VILLAGE': '//*[@id="side_info"]//*[contains(text(), "%s")]',
            'SELECTED_VILLAGE': '//*[@id="side_info"]//*[@class="dot h1"]//a',
            'ALL_VILLAGES_LINKS': '//*[@id="vlist"]//*[@class="link"]//a',
            'VILLAGE_NAME': '//*[@id="content"]/h1',
            'SEND_GOODS': '//*[@id="side_info"]//*[contains(text(), "%s")]/../../../..//*[contains(text(), "Send goods")]',
            'SEND_TROOPS': '//*[@id="side_info"]//*[contains(text(), "%s")]/../../../..//*[contains(text(), "Send troops!")]',
            #
            # OVillage
            #
            'LEVEL_UP_CONE': '//*[@id="cone"]',
            'INSTRUCTIONS_COSTS': '//*[@CLASS="dur"]/..',
            #
            # Gold
            #
            'GOLD_AMOUNT': '//*[@id="side_navi"]//[@class="gold"]/..',
            'PLUS_MENU': '//*[@id="side_navi"]//*[contains(text(), "Zravian Plus")]',
            'PLUS_MENU_ACTIVATE_OPT': '//*[@class="plusFunctions"]//*[contains(text(), "%s")]/../*[@class="act"]/a',
            'PLUS_MENU_OPT_TIME_LEFT': '//*[@class="plusFunctions"]//*[contains(text(), "%s")]/../*[@class="run"]',
            'PLUS_MENU_OPT_COST': '//*[@class="plusFunctions"]//*[contains(text(), "%s")]/../*[@class="cost"]',
            #
            # Alliance
            #
            'ALLIANCE_TAG_INPUT': '//input[@name="ally1"]',
            'ALLIANCE_NAME_INPUT': '//input[@name="ally2"]',
            'ALLIANCE_OK_BTN': '//*[@id="btn_ok"]',
            'ALLIANCE_ACCEPT_BTN': '//a[text()="%s"]/../../*[@class="acc"]/a',
            'ALLIANCE_CURRENT_TAG': '//*[contains(text(), the Alliance)]/../../..//*[contains(text(), "%s")]',
            'ALLIANCE_TAG_ERROR': '//*[contains(text(), "That tag is already taken")]',
            #
            # Overview
            #
            'OVERVIEW_TROOPS': '//*[@id="troops"]',
            #
            # Statistics
            #
            'STATISTICS_MY_RANKING': '//*[@id="player"]//*[@class="hl"]//*[@class="ra"]',
            'STATISTICS_ACCOUNT': '//*[@id="player"]//*[@class="hl"]//*[@class="pla"]/a',
            #
            # Map
            #
            'VILLAGE_BY_NAME': '//area[contains(@alt, "%s")]',
            #
            # Missions
            #
            'TASK_MASTER': '//*[@id="qgei"]',
            'MISSION_DIALOG': '//*[@class="popup3 quest"]',
            'MISSION_DIALOG_STATUS': '//*[@id="anm"]',
            'MISSION_CLOSE_BTN': '//*[@class="popup4"]',
            'MISSION_NAME': '//*[@id="qstd"]/h1',
            'MISSION_TEXT_BOX': '//*[@id="qst_val"]',
            'MISSION_CONFIRM': '//*[@id="qstd"]//input[@value="Confirm"]',
            'MISSION_COORD_X': '//*[@id="qst_val_x"]',
            'MISSION_COORD_Y': '//*[@id="qst_val_y"]',
            'MISSION_SEND_WHEAT_BTN': '//*[@id="qstd"]//input[@value="Send wheat"]',
            'MISSION_REINFORCEMENT_RAT': '//*[@id="troops"]//*[@alt="Rat"]',
            'MISSION_CHOOSE_ARMY': '//*[@id="qstd"]/input[@value="Army"]',
            'MISSION_CHOOSE_ECONOMY': '//*[@id="qstd"]/input[@value="Economy"]',
            'ACCOMPLISH_MISSION': '//*[contains(text(), "Continue with the next task")]',
            'SKIPPED_MISSION_INVOKE_BTN': '//*[text()="invoke"]',
            'SKIPPED_MISSION_REWARD_DESC': '//*[text()="invoke"]/../../..//*[@class="desc"]',
            'SKIPPED_MISSION_REWARD_RESOURCES': '//*[text()="invoke"]/../../..//*[@class="desc"]',
            'SKIPPED_MISSION_REWARD_TIMEOUT': '//*[text()="invoke"]/../../..//*[@class="dur"]',
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
            # Menu
            'BUILDING_PAGE_TITLE': '//*[@id="build"]//*[contains(text(), "%s")]',
            'BUILDING_PAGE_EMPTY_TITLE': '//*[contains(text(), "Construct building.")]',
            'BUILDING_MENU_TITLE': '//*[@id="build"]/h1',
            # Construct new building menu
            'CONSTRUCT_BUILDING_NAME': '//*[contains(@alt, "%s")]/../../../..',
            'CONSTRUCT_BUILDING_BTN': '//*[contains(text(), "Construct buildings")]',
            # Constructing/Leveling up errors
            'CONSTRUCT_ERR_WRAPPER': '//*[@id="new_building"]',
            'LEVEL_UP_ERR_WRAPPER': '//*[@id="contract"]',
            'BUILDING_ERR_RESOURCES': '//*[contains(text(), "Enough resources in")]',
            'BUILDING_ERR_WH': '//*[contains(text(), "Upgrade your warehouse")]',
            'BUILDING_ERR_GR': '//*[contains(text(), "Upgrade your granary")]',
            'BUILDING_ERR_BUSY_WORKERS': '//*[contains(text(), "Your builders are already working")]',
            'BUILDING_ERR_MAX_LVL': '//*[contains(text(), "fully upgraded")]',
            # Costs
            'LEVEL_UP_COSTS': '//*[@id="contract"]',
            'CONSTRUCT_COSTS': '//*[@class="res"]',
            # SUCCESSFUL UPGRADE
            'CONSTRUCT_BUILDING_ID': '//*[contains(text(), "Construct buildings")]',
            'LEVEL_UP_BUILDING_BTN': '//*[contains(text(), "Upgrade to level")]',
            # DEMOLITION
            'DEMOLITION_BUILDING_OPTION': '//*[contains(text(), "%d.")]',
            'DEMOLITION_BTN': '//*[@id="btn_demolish"]',
            #
            # Marketplace
            #
            'SEND_LUMBER_INPUT_BOX': '//*[@id="send_select"]//*[contains(text(), "Lumber")]//input',
            #
            # Academy
            #
            'RESEARCH_TROOP': '//*[contains(text(), "%s")]/../../..//*[contains(text(), "Research")]',
            # Research errors
            'RESEARCH_ERR_RESOURCES': '//*[contains(text(), "%s")]/../../..//*[contains(text(), "Not enough resources")]',
        }
        for key, value in self.objects.items():
            self.__setitem__(key, value)


# All tribes
class Tribe(Enum):
    ROMANS = 'ROMANS'
    TEUTONS = 'TEUTONS'
    GAULS = 'GAULS'
    

# All buildings
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
    Treasury = 27
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
    WonderOfTheWorld = 40
    HorseDrinkingPool = 41


# All units
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


# All resource types
class ResourceType(Enum):
    LUMBER = 'lumber'
    CLAY = 'clay'
    IRON = 'iron'
    CROP = 'crop'


# Requirement named tuple
BuildingRequirement = namedtuple(typename='BuildingRequirement', field_names=['buildingType', 'level'])

# Special requirement named tuple
class SRType(Enum):
    ARTIFACT = 'ARTIFACT'
    NO_CAPITAL = 'NO CAPITAL'
    NO_RESIDENCE = 'NO Residence'
    NO_PALACE = 'NO Palace'
    NO_WW = 'NO Wonder of the World'
    TRIBE_ROMANS = 'TRIBE ROMANS'
    TRIBE_TEUTONS = 'TRIBE TEUTONS'
    TRIBE_GAULS = 'TRIBE GAULS'

SpecialRequirement = namedtuple(typename='SpecialRequirement', field_names=['type'])


# Class containing building properties
class BuildingInfo:
    def __init__(self, data):
        # Keywork in special requirements
        self.id = data['id']
        self.type = BuildingType(self.id)
        self.name = data['name']
        self.maxLevel = data['maxLevel']
        self.requirements = []
        for building, level in data['requirements']:
            self.requirements.append(BuildingRequirement(get_building_type_by_name(building), int(level)))
        self.specialRequirements = []
        for value in data['specialRequirements']:
            for sr in SRType:
                if value == sr.value:
                    self.specialRequirements.append(sr)
                    break
        self.duplicates = data['duplicates']


# Named tuple 
Building = namedtuple(typename='Building', field_names=['siteId', 'level'])


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
def init_data():
    """
    Initialises constants by parsing data.json.
    """
    global TROOPSInstance
    global BUILDINGS_DATA_Instance
    # Init
    BUILDINGS_DATA_Instance = {}
    TROOPSInstance = {}
    # Read data
    with open(DATA_PATH, 'r') as f:
        jsonData = f.read()
    # Populate buildings
    buildings = json.loads(jsonData)['buildings']
    assert len(buildings) == len(BuildingType)
    for bdType, bdData in zip(BuildingType, buildings):
        assert bdType == bdData['id']
        BUILDINGS_DATA_Instance[bdType] = BuildingInfo(bdData)
    # Populate troops
    troops = json.loads(jsonData)['troops']['romans']
    troops += json.loads(jsonData)['troops']['teutons']
    troops += json.loads(jsonData)['troops']['gauls']
    assert len(troops) == len(TroopType)
    for troopType, troopData in zip(TroopType, troops):
        troopName = ' '.join(troopType.name.split('_'))
        assert troopName == troopData['name'] or troopName[1:] == troopData['name']
        TROOPSInstance[troopType] = Troop(troopData, troopType)


def get_building_info(bdType : BuildingType) -> BuildingInfo:
    """
    Building data for required building if it exists.

    Instantiates BUILDINGS_DATA_Instance if needed.
    
    Returns:
        - Building data object.
    """
    if BUILDINGS_DATA_Instance is None:
        init_data()
    return BUILDINGS_DATA_Instance[bdType]


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


def get_projectLogger():
    """
    Returns:
        - The Project Logger Singleton.
    """
    return logger
