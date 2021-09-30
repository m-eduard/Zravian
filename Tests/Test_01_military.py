import pytest
import sys
import time

sys.path.append('../')

from Framework.military.academy import TROOPS
from Framework.utility.SeleniumWebScraper import SWS, Attr
from Framework.infrastructure.builder import enter_building
from Framework.utility.Constants import BuildingType, Server, TroopType
from Framework.account.Login import XPATH, login
from Framework.military.troops_trainer import make_troops_by_amount, reduce_train_time, troop_max_amount

# def setup_module():
# 	global sws
# 	global sws_generator
# 	sws_generator = login(Server.S10k, username="0bomb15", headless=True)
# 	sws = next(sws_generator)
# 	assert sws is not None

# def teardown_module():
# 	global sws
# 	global sws_generator
# 	if sws:
# 		sws_generator.close()
# 	sws = None

def get_tpType_by_name(literalName : str):
	tpType = None

	for i in TroopType:
		if TROOPS[i].name == literalName:
			tpType = i
			break
	
	return tpType

class Test_01_military:
	def test_01_military_01(self):
		"""
		Id: 01
		Description: Test if troops' training can be done properly in every training building
		Steps:
			1. Go in every building that supports train troops operation.
			2: Extract the names of all trainable troops.
			3. Extract the maximum amount of units that can be trained.
			4. Sometimes, go in other building than the one where you can train troops
			5. Call make_troops_by_amount() for every troop that can be trained in a building, using a valid amount.
		Objectives:
			5. make_troops_by_amount() should return True for every call.
		"""
		with login(Server.S10k, username="0bomb15", headless=True) as sws:
			buildings = [BuildingType.Barracks, BuildingType.SiegeWorkshop, BuildingType.Stable]

			for bdType in buildings:
				# S1: Enter in every building that can train troops.
				assert enter_building(sws, bdType)

				# S2: Extract the names of all trainable troops.
				troops = sws.getElementsAttribute('//table[@class="build_details"]//*[@class="tit"]//a', Attr.TEXT)

				for i in range(len(troops)):
					#S3: Get the maximum amount.
					max = troop_max_amount(sws, get_tpType_by_name(troops[i]))

					#S4: Sometimes, go in other building than the one where you can train troops
					if i % 2 == 0:
						enter_building(sws, BuildingType.Brewery)

					#S5: Call make_troops_by_amount() for every troop.
					#O5: make_troops_by_amount() should return only True
					assert make_troops_by_amount(sws, get_tpType_by_name(troops[i]), int(max % 1000))

	# reduce train time button should be available in order to run successfully this test
	def test_01_military_02(self):
		"""
		Id: 03
		Description: Test reduce_train_time()
		Steps:
			1. Start from an initial phase (no troops are training).
			2. Call make_troops_by_amount() for every building that supports training troops.
			3. Call reduce_train_time() before leaving a building.		
			4. Check if training troops table exists.
		Objectives:
			4. After calling reduce_train_time(), if was successful, then no troops should be currently training (so no table).
		"""
		with login(Server.S10k, username="0bomb15", headless=True) as sws:
			buildings = [BuildingType.Barracks, BuildingType.Stable, BuildingType.SiegeWorkshop]

			#S1: Wait for the initial phase.
			for bdType in buildings:
				enter_building(sws, bdType)
				while sws.isVisible('//*[@class="under_progress"]'):
					time.sleep(15)

			for bdType in buildings:
				assert enter_building(sws, bdType)
				troops = sws.getElementsAttribute('//table[@class="build_details"]//*[@class="tit"]//a', Attr.TEXT)

				for i in troops:
					max = troop_max_amount(sws, get_tpType_by_name(i))

					#S2: Call make_troops_by_amount() for every troop.
					assert make_troops_by_amount(sws, get_tpType_by_name(i), int(max % 1000))


				#S3: Call reduce_train_time() before leaving a building.
				if reduce_train_time(sws, bdType) is True:
					#S4: Check if training troops table exists.
					#O4: No training troops tables should be visible
					assert sws.isVisible('//*[@class="under_progress"]') == False
