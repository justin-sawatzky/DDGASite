#!/opt/env/bin/ python
import boto3
import pprint

from boto3.dynamodb.conditions import Attr
from flask import Flask, render_template


app = Flask(__name__)


HAPPYLAND = 'Happyland Park'
HAPPYLAND_COUNT = 6
KILCONA = 'Kilcona Lakes'
KILCONA_COUNT = 2
LABARRIERE = 'LaBarriere Disc Golf Course'
LABARRIERE_COUNT = 2


def _read_all_scores(scores_table, player_name=None):
    scores = []

    if player_name:
        response = scores_table.scan(FilterExpresion=Attr('PlayerName').eq(player_name))
    else:
        response = scores_table.scan()
    scores += response['Items']

    while 'LastEvaluatedKey' in response:
        response = scores_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        scores += response['Items']

    return scores


def _group_scores_per_course(scores):
    course_scores = {}
    for score in scores:
        key = f"{score['PlayerName']} {score['CourseName']}"
        if key in course_scores:
            course_scores[key].append(score)
        else:
            course_scores[key] = [score]

    return {key: sorted(scores, key=lambda score: int(score['+/-'])) for key, scores in course_scores.items()}


def _trim_scores(course_scores):
    for key, scores in course_scores.items():
        if HAPPYLAND in key:
            course_scores[key] = scores[:6]
        elif KILCONA in key:
            course_scores[key] = scores[:2]
        elif LABARRIERE in key:
            course_scores[key] = scores[:2]


def _get_rankings(course_scores):
    def _get_player_scores(player_name, player_scores):
        for course, count in [(HAPPYLAND, HAPPYLAND_COUNT), (KILCONA, KILCONA_COUNT), (LABARRIERE, LABARRIERE_COUNT)]:
            league_course_rounds = [int(score['+/-']) for key, scores in course_scores.items() if player_name in key and course in key for score in scores]
            league_course_rounds += ['-'] * (count - len(league_course_rounds))

            player_scores.extend(league_course_rounds)

    players = [
        'Justin',
        'CHall',
        'Juice',
        'Tom',
        'Ryan',
        'Tyler'
    ]
    rankings = []

    for player in players:
        player_scores = [player]
        player_scores.append(sum([int(score['+/-']) for key, scores in course_scores.items() if player in key for score in scores]))
        _get_player_scores(player, player_scores)
        
        rankings.append(player_scores)

    return sorted(rankings, key=lambda x: x[1])


@app.route('/')
def home_page():
    dynamo = boto3.resource('dynamodb', region_name='ca-central-1')
    scores_table = dynamo.Table('ddga_player_scores')

    course_scores = _group_scores_per_course(_read_all_scores(scores_table))
    _trim_scores(course_scores)
    
    return render_template(
        'scores_table.html', 
        ranked_player_scores=_get_rankings(course_scores)
    )


@app.route('/scores/<player_name>')
def player_scores_page(player_name):
    dynamo = boto3.resource('dynamodb', region_name='ca-central-1')
    scores_table = dynamo.Table('ddga_player_scores')

    course_scores = _group_scores_per_course(_read_all_scores(scores_table))
    happyland_course_scores = course_scores[f'{player_name} {HAPPYLAND}']
    kilcona_course_scores = course_scores[f'{player_name} {KILCONA}']
    labarriere_course_scores = course_scores[f'{player_name} {LABARRIERE}']

    headers = [
        'Date',
        'Total',
        '+/-',
        'Hole1',
        'Hole2',
        'Hole3',
        'Hole4',
        'Hole5',
        'Hole6',
        'Hole7',
        'Hole8',
        'Hole9',
        'Hole10',
        'Hole11',
        'Hole12',
        'Hole13',
        'Hole14',
        'Hole15',
        'Hole16',
        'Hole17',
        'Hole18'
    ]
    
    return render_template(
        'player_scores.html', 
        player_name=player_name,
        headers=headers,
        happyland_course_scores=happyland_course_scores,
        kilcona_course_scores=kilcona_course_scores,
        labarriere_course_scores=labarriere_course_scores
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
