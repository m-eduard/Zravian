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
from Framework.military.upgrade_troops import upgrade_troop_defense, upgrade_troop_offense
from Framework.military.heros_mansion import name_hero, train_hero

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
		with login(Server.S10k, username="0bomb15", headless=False) as sws:
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
						enter_building(sws, BuildingType.MainBuilding)

					#S5: Call make_troops_by_amount() for every troop.
					#O5: make_troops_by_amount() should return only True
					assert make_troops_by_amount(sws, get_tpType_by_name(troops[i]), max % 1000)

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
					assert make_troops_by_amount(sws, get_tpType_by_name(i), max % 1000)


				#S3: Call reduce_train_time() before leaving a building.
				if reduce_train_time(sws, bdType) is True:
					#S4: Check if training troops table exists.
					#O4: No training troops tables should be visible
					assert sws.isVisible('//*[@class="under_progress"]') == False

	def test_01_military_03(self):
		"""
		Id: 03
		Description: Test upgrade_troop_defense() / upgrade_troop_offense()
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

	def test_01_military_03(self):
		"""
		Id: 03
		Description: Test upgrade_troop_defense() / upgrade_troop_offense()
		Steps:
			1. Get the current level for the first troop that supports upgrade
			2. Call the forespoken functions for the selected troop
		Objectives:
			2. The level should be increased, if the action was possible
		"""
		with login(Server.S10k, username="0bomb15", headless=True) as sws:
			ls = ['defense', 'offense']
			for upgradeType in ls:
				test = upgradeType

				if test == 'offense':
					assert enter_building(sws, BuildingType.Blacksmith)
				else:
					assert enter_building(sws, BuildingType.Armoury)

				troopsStatus = sws.getElementsAttribute('//*[@class="build_details"]//tbody//*[@class="act"]', Attr.TEXT)
				troopsName = sws.getElementsAttribute('//*[@class="build_details"]//tbody//*[@class="desc"]//a', Attr.TEXT)

				# S1: Get the current level for the first troop that supports upgrade
				index = -1
				for i in range(len(troopsStatus)):
					if troopsStatus[i] == 'Upgrade':
						index = i
						break

				if index != -1:
					troop = get_tpType_by_name(troopsName[index])
					currentLevel = sws.getElementAttribute(f'//*[@class="build_details"]\
															//tr[{index + 1}]//*[@class="info"]', Attr.TEXT)
					currentLevel = currentLevel.split()
					currentLevel = int(currentLevel[-1][:-1])

					notLast = True
					if currentLevel == 19:
						notLast = False

					# S2: Call the tested functions, one at a time
					if test == 'offense':
						assert upgrade_troop_offense(sws, troop, True)
					else:
						assert upgrade_troop_defense(sws, troop, True)

					# O2: Check if the troop's level was increased
					if notLast:
						newLevel = sws.getElementAttribute(f'//*[@class="build_details"]\
																//tr[{index + 1}]//*[@class="info"]', Attr.TEXT)
						newLevel = newLevel.split()
						newLevel = int(newLevel[-1][:-1])
						assert newLevel - currentLevel == 1
					else:
						size = len(sws.getElementsAttribute('//*[@class="build_details"]//tbody//*[@class="act"]', Attr.TEXT))
						assert len(troopsStatus) - size == 1

		
	def test_01_military_04(self):
		"""
		Id: 04
		Description: Test name_hero()
		Steps:
			1. Call the name_hero() using a random string as the new name.
			2. Refresh the page and get the current hero name.
		Objectives:
			2. The new hero name should match the random string sent as parameter
			   to name_hero()
		"""
		with login(Server.S10k, username="0bomb15", headless=True) as sws:
			assert enter_building(sws, BuildingType.HeroMansion)
			train_hero(sws, TroopType.Clubswinger)

			# S1: Call the name_hero() using a random string as the new name
			generatedName = str(time.time())
			generatedName = generatedName[:20]
			assert name_hero(sws, generatedName)

			# S2: Refresh the page and get the current hero name.
			sws.refresh()
			newName = sws.getElementAttribute(XPATH.HERO_NAME, Attr.VALUE)

			# O2: The new hero name should match the random string sent as parameter
			#     to name_hero()
			assert newName == generatedName
