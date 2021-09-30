from Framework.infrastructure.builder import enter_building
from Framework.utility.Constants import  BuildingType, TroopType, get_TROOPS, get_XPATH, get_projectLogger
from Framework.utility.SeleniumWebScraper import SWS, Attr
from time import sleep

logger = get_projectLogger()
TROOPS = get_TROOPS()
XPATH = get_XPATH()

def upgrade_troop(sws : SWS, tpType : TroopType, bdType : BuildingType):
	"""
	Upgrade the speciefied troop inside the specified building

	Parameters:
		- sws (SWS): Selenium Web Scraper.
		- tpType (TroopType): Denotes troop.
		- bdType (BuildingType): Denotes the building where you want to upgrade the troop.

	Returns:
		- True if the operation is successful, False otherwise.
	"""
	status = False

	target_buildings = [BuildingType.Armoury, BuildingType.Blacksmith]

	if bdType in target_buildings:
		enter_building(sws, bdType)

		if sws.clickElement(XPATH.UPGRADE_BTN % TROOPS[tpType].name, refresh=True):
			logger.success(f'In function upgrade_troop: {TROOPS[tpType].name} was upgraded')
			status = True
		else:
			logger.error('In function upgrade_troop: Failed to press upgrade')
	else:
		logger.error('In function upgrade_troop: Received an invalid bdType parameter')
	
	return status
