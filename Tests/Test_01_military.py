import pytest
import sys

sys.path.append('../')

from Framework.infrastructure.builder import enter_building
from Framework.utility.Constants import Building, BuildingType, Server, TroopType
from Framework.account.Login import login
from Framework.military.troops_trainer import make_troops_by_amount

class Test_01_military:
	# perform this test on an account that can train at least one type of troop
	# in the barracks
	def test_01_military_01(self):
		with login(Server.S10k, username="0bomb15", headless=False) as sws:
			assert enter_building(sws, BuildingType.Barracks)

			troops = sws.getElementsAttribute('//table[@class="build_details"]//*[@class="tit"]//a', 'text')
			max = sws.getElementAttribute('//table[@class="build_details"]//*[@class="max"]', 'text')

			half = [int(x) / 2 for x in max]

			# test make_troops_by_amount() for every troop that can be trained in the barracks,
			# for half of the maximum amount trainable (because all max values are extracted before
			# training any troops, at some point, there may not be enough resources to train any troops)
			for i in range(len(troops)):
				make_troops_by_amount(sws, getattr(TroopType, troops[i]), half[i])
