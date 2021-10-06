from Framework.infrastructure.builder import enter_building
from Framework.utility.Constants import  BuildingType, TroopType, get_TROOPS, get_XPATH, get_projectLogger, time_to_seconds
from Framework.utility.SeleniumWebScraper import SWS, Attr
from time import sleep

logger = get_projectLogger()
TROOPS = get_TROOPS()
XPATH = get_XPATH()

def upgrade_troop_offense(sws : SWS, tpType : TroopType, waitFor : bool = False):
	"""
	Upgrade the specified troop's offense.

	Parameters:
		- sws (SWS): Selenium Web Scraper.
		- tpType (TroopType): Denotes troop.
		- waitFor (bool): If it's True, it waits until the requested troop upgrade is done;
						  else, after sending the upgrade signal, the function ends

	Returns:
		- True if the operation is successful, False otherwise.
	"""
	status = __upgrade_troop(sws, tpType, BuildingType.Blacksmith, 'upgrade_troop_offense')
	if waitFor:
		sleep(get_update_time(sws, tpType) + 0.1)
	return status


def upgrade_troop_defense(sws : SWS, tpType : TroopType, waitFor : bool = False):
	"""
	Upgrade the specified troop's defense.

	Parameters:
		- sws (SWS): Selenium Web Scraper.
		- tpType (TroopType): Denotes troop.
		- waitFor (bool): If it's True, it waits until the requested troop upgrade is done;
						  else, after sending the upgrade signal, the function ends

	Returns:
		- True if the operation is successful, False otherwise.
	"""
	status = __upgrade_troop(sws, tpType, BuildingType.Armoury, 'upgrade_troop_defense')
	if waitFor:
		sleep(get_update_time(sws, tpType) + 0.1)
	return status


def __upgrade_troop(sws : SWS, tpType : TroopType, bdType : BuildingType, functionName : str):
	status = False
	target_buildings = [BuildingType.Armoury, BuildingType.Blacksmith]
	if bdType in target_buildings:
		if enter_building(sws, bdType):
			if sws.clickElement(XPATH.UPGRADE_BTN % TROOPS[tpType].name, refresh=True):
				logger.success(f'In function {functionName}: {TROOPS[tpType].name} was upgraded')
				status = True
			else:
				logger.error(f'In function {functionName}: Failed to press upgrade')
		else:
			logger.error(f'In {functionName}: Failed to enter {bdType}')
	else:
		logger.error(f'In function {functionName}: Received an invalid bdType parameter')
	return status


def get_update_time(sws : SWS, tpType : TroopType):
	"""
	Get the time until the specified troop is upgraded.

	Parameters:
		- sws (SWS): Selenium Web Scraper.
		- tpType (TroopType): Denotes troop.

	Returns:
		- time in seconds
	"""
	time = sws.getElementAttribute(XPATH.UPGRADE_TIME % TROOPS[tpType].name, Attr.TEXT)
	if time == None or time[-1] == '?':
		time = 0
	else:
		time = time_to_seconds(time)
	return time
