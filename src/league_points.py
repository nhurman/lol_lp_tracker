from cassiopeia.type.core.common import Queue
from cassiopeia import riotapi
from cassiopeia.type.api.exception import APIError


class SummonerNotFoundException(Exception):
	pass


class LeagueNotFoundException(Exception):
	pass


def get_lp(summoner_id):
	try:
		summoner = riotapi.get_summoner_by_id(summoner_id)
	except APIError:
		raise SummonerNotFoundException

	try:
		summoner_leagues = riotapi.get_league_entries_by_summoner(summoner)
	except APIError:
		raise LeagueNotFoundException

	try:
		queue = next(league for league in summoner_leagues if league.queue == Queue.ranked_solo)
	except StopIteration:
		raise LeagueNotFoundException

	entry = queue.entries[0]
	league_data = [queue.tier, entry.division, entry.league_points]
	return league_data
