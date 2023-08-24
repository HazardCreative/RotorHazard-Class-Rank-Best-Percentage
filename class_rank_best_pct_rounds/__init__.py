''' Class ranking method: Laps/Time, Best % rounds '''

import logging
import RHUtils
import math
from eventmanager import Evt
from RHRace import StartBehavior
from Results import RaceClassRankMethod
from RHUI import UIField, UIFieldType, UIFieldSelectOption

logger = logging.getLogger(__name__)

def rank_best_pct_rounds(rhapi, race_class, args):
    if 'round_pct' not in args or not args['round_pct'] or int(args['round_pct']) < 1:
        return False, {}

    round_pct = float(args['round_pct']) / 100

    race_format = rhapi.db.raceformat_by_id(race_class.format_id)
    heats = rhapi.db.heats_by_class(race_class.id)

    pilotresults = {}
    for heat in heats:
        races = rhapi.db.races_by_heat(heat.id)

        for race in races:
            race_result = rhapi.db.race_results(race)

            if race_result:
                for pilotresult in race_result['by_race_time']:
                    if pilotresult['pilot_id'] not in pilotresults:
                        pilotresults[pilotresult['pilot_id']] = []
                    pilotresults[pilotresult['pilot_id']].append(pilotresult)
            else:
                logger.warning("Failed building ranking, race result not available")
                return False, {}

    leaderboard = []
    for pilotresultlist in pilotresults:
        if race_format and race_format.start_behavior == StartBehavior.STAGGERED:
            pilot_result = sorted(pilotresults[pilotresultlist], key = lambda x: (
                -x['laps'], # reverse lap count
                x['total_time_laps_raw'] if x['total_time_laps_raw'] and x['total_time_laps_raw'] > 0 else float('inf') # total time ascending except 0
            ))
        else:
            pilot_result = sorted(pilotresults[pilotresultlist], key = lambda x: (
                -x['laps'], # reverse lap count
                x['total_time_raw'] if x['total_time_raw'] and x['total_time_raw'] > 0 else float('inf') # total time ascending except 0
            ))

        if 'rounding' not in args or args['rounding'] == 'down':
            rounds = int(len(pilot_result) * round_pct)
        elif args['rounding'] == 'nearest': 
            rounds = round(len(pilot_result) * round_pct)
        else: # up
            rounds = math.ceil(len(pilot_result) * round_pct)

        pilot_result = pilot_result[:rounds]

        new_pilot_result = {}
        new_pilot_result['pilot_id'] = pilot_result[0]['pilot_id']
        new_pilot_result['callsign'] = pilot_result[0]['callsign']
        new_pilot_result['team_name'] = pilot_result[0]['team_name']
        new_pilot_result['node'] = pilot_result[0]['node']
        new_pilot_result['laps'] = 0
        new_pilot_result['starts'] = 0
        new_pilot_result['total_time_raw'] = 0
        new_pilot_result['total_time_laps_raw'] = 0

        for race in pilot_result:
            new_pilot_result['laps'] += race['laps']
            new_pilot_result['starts'] += race['starts']
            new_pilot_result['total_time_raw'] += race['total_time_raw']
            new_pilot_result['total_time_laps_raw'] += race['total_time_laps_raw']

        timeFormat = rhapi.db.option('timeFormat')
        new_pilot_result['total_time'] = RHUtils.time_format(new_pilot_result['total_time_raw'], timeFormat)
        new_pilot_result['total_time_laps'] = RHUtils.time_format(new_pilot_result['total_time_laps_raw'], timeFormat)

        leaderboard.append(new_pilot_result)

    if race_format and race_format.start_behavior == StartBehavior.STAGGERED:
        # Sort by laps time
        leaderboard = sorted(leaderboard, key = lambda x: (
            -x['laps'], # reverse lap count
            x['total_time_laps_raw'] if x['total_time_laps_raw'] and x['total_time_laps_raw'] > 0 else float('inf') # total time ascending except 0
        ))

        # determine ranking
        last_rank = None
        last_rank_laps = 0
        last_rank_time = 0
        for i, row in enumerate(leaderboard, start=1):
            pos = i
            if last_rank_laps == row['laps'] and last_rank_time == row['total_time_laps_raw']:
                pos = last_rank
            last_rank = pos
            last_rank_laps = row['laps']
            last_rank_time = row['total_time_laps_raw']

            row['position'] = pos

        meta = {
            'rank_fields': [{
                'name': 'laps',
                'label': "Laps"
            },{
                'name': 'total_time_laps',
                'label': "Total"
            },{
                'name': 'starts',
                'label': "Starts"
            }]
        }

    else:
        # Sort by race time
        leaderboard = sorted(leaderboard, key = lambda x: (
            -x['laps'], # reverse lap count
            x['total_time_raw'] if x['total_time_raw'] and x['total_time_raw'] > 0 else float('inf') # total time ascending except 0
        ))

        # determine ranking
        last_rank = None
        last_rank_laps = 0
        last_rank_time = 0
        for i, row in enumerate(leaderboard, start=1):
            pos = i
            if last_rank_laps == row['laps'] and last_rank_time == row['total_time_raw']:
                pos = last_rank
            last_rank = pos
            last_rank_laps = row['laps']
            last_rank_time = row['total_time_raw']

            row['position'] = pos

        meta = {
            'rank_fields': [{
                'name': 'laps',
                'label': "Laps"
            },{
                'name': 'total_time',
                'label': "Total"
            },{
                'name': 'starts',
                'label': "Starts"
            }]
        }

    return leaderboard, meta

def register_handlers(args):
    args['register_fn'](
        RaceClassRankMethod(
            "Laps/Time: Best % Rounds",
            rank_best_pct_rounds,
            {
                'round_pct': 50
            },
            [
                UIField('round_pct', "Percentage of rounds", UIFieldType.BASIC_INT, placeholder="50"),
                UIField('rounding', "Rounding", UIFieldType.SELECT, options=[
                        UIFieldSelectOption('down', "Down"),
                        UIFieldSelectOption('nearest', "Nearest"),
                        UIFieldSelectOption('up', "Up"),
                    ], value='down'),
            ]
        )
    )

def initialize(rhapi):
    rhapi.events.on(Evt.CLASS_RANK_INITIALIZE, register_handlers)

