import xml.etree.ElementTree as ET
from sleekxmpp import ClientXMPP
import re
import league_points

from cassiopeia.type.core.common import Tier, Division


class Regions:
	EUW = ('chat.euw1.lol.riotgames.com', 5223)


class Monitor(ClientXMPP):
	def __init__(self, server, username, password):
		self._tracked_summoners = set()
		self._summoner_id_re = re.compile(r'^sum(\d+)@pvp.net$')

		resource = 'lol_lp_tracker'
		jabber_id = '{0}@pvp.net/{1}'.format(username, resource)
		password = 'AIR_' + password
		ClientXMPP.__init__(self, jabber_id, password)

		self.add_event_handler("session_start", self.session_start)
		self.add_event_handler("roster_update", self.roster_update)
		self.add_event_handler("presence", self.presence_update)

		self._expected_server_name = server[0]
		self.connect(server, use_tls=False, use_ssl=True)

	def set_status(self, message):
		root = ET.Element('body')
		ET.SubElement(root, 'profileIcon').text = "1"
		ET.SubElement(root, 'level').text = "30"
		ET.SubElement(root, 'wins').text = "0"
		ET.SubElement(root, 'leaves').text = "0"
		ET.SubElement(root, 'odinWins').text = "0"
		ET.SubElement(root, 'odinLeaves').text = "0"
		ET.SubElement(root, 'queueType').text = ""
		ET.SubElement(root, 'rankedLosses').text = "0"
		ET.SubElement(root, 'rankedRating').text = "0"
		ET.SubElement(root, 'tier').text = "UNRANKED"
		ET.SubElement(root, 'rankedSoloRestricted').text = "false"
		ET.SubElement(root, 'championMasteryScore').text = "0"
		ET.SubElement(root, 'statusMsg').text = message
		ET.SubElement(root, 'isObservable').text = "ALL"
		ET.SubElement(root, 'dropInSpectateGameId').text = ""
		ET.SubElement(root, 'featuredGameData').text = "null"
		ET.SubElement(root, 'rankedLeagueName').text = ""
		ET.SubElement(root, 'rankedLeagueDivision').text = ""
		ET.SubElement(root, 'rankedLeagueTier').text = "UNRANKED"
		ET.SubElement(root, 'rankedLeagueQueue').text = ""
		ET.SubElement(root, 'rankedWins').text = "0"
		ET.SubElement(root, 'skinname').text = ""
		ET.SubElement(root, 'gameQueueType').text = ""
		ET.SubElement(root, 'gameStatus').text = "outOfGame"
		ET.SubElement(root, 'timeStamp').text = "0"

		xml = ET.tostring(root).decode('utf-8')
		self.send_presence(pshow="away", pstatus=xml)

	def session_start(self, iq):
		self.set_status("LPTracker bot")

	def roster_update(self, iq):
		pass

	def presence_update(self, presence):
		xmpp_id = presence.values['from'].bare
		status = self.parse_status(presence.values['status'])

		if status is None:
			pass
		elif status[0] == 'inGame':
			if status[1] == 'RANKED_SOLO_5x5':
				self._tracked_summoners.add(xmpp_id)
		elif xmpp_id in self._tracked_summoners:
			self._tracked_summoners.remove(xmpp_id)
			self.get_lp(xmpp_id)

	def get_lp(self, xmpp_id):
		groups = self._summoner_id_re.match(xmpp_id)
		if groups is None:
			return

		id = groups.group(1)

		try:
			ranked_info = league_points.get_lp(id)
			points = self.calculate_points(ranked_info)
			print('{0} has {1} points'.format(id, points))
		except league_points.SummonerNotFoundException:
			print('Error: Summoner not found')
		except league_points.LeagueNotFoundException:
			print('Error: Solo ranked league not found')

	@staticmethod
	def calculate_points(ranked_info):
		tier_points = {
			Tier.bronze: 0,
			Tier.silver: 500,
			Tier.gold: 1000,
			Tier.platinum: 1500,
			Tier.diamond: 2000,
			Tier.master: 2500,
			Tier.challenger: 2500
		}

		division_points = {
			Division.five: 0,
			Division.four: 100,
			Division.three: 200,
			Division.two: 300,
			Division.one: 400
		}

		points = tier_points[ranked_info[0]]
		if ranked_info[0] not in [Tier.master, Tier.challenger]:
			points += division_points[ranked_info[1]]
		points += ranked_info[2]

		return points

	@staticmethod
	def parse_status(status):
		try:
			xml = ET.fromstring(status)
		except ET.ParseError:
			return None

		game_status = xml.find('./gameStatus')
		if game_status is not None:
			game_status = game_status.text

		queue_type = xml.find('./gameQueueType')
		if queue_type is not None:
			queue_type = queue_type.text

		return [game_status, queue_type]
