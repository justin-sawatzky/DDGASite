#!/opt/env/bin/ python
import boto3

from flask import Flask, render_template


app = Flask(__name__)


def _read_all_scores(scores_table):
    scores = []

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

    return {key: sorted(scores, key=lambda score: score['Total']) for key, scores in course_scores.items()}


def _trim_scores(course_scores):
    for key, scores in course_scores.items():
        if 'Happyland Park' in key:
            course_scores[key] = scores[:6]
        elif 'Kilcona Lakes' in key:
            course_scores[key] = scores[:2]
        elif 'LaBarriere Disc Golf Course' in key:
            course_scores[key] = scores[:2]


def _get_rankings(course_scores):
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
        score = sum([int(score['+/-']) for key, scores in course_scores.items() if player in key for score in scores])
        rankings.append((player, score))

    return sorted(rankings, key=lambda x: x[1])   


def _generate_response(rankings):
    ranking_str = ''

    for rank in range(len(rankings)):
        ranking_str += f'<p>{rank+1}) {rankings[rank][0]} {rankings[rank][1]}</p>'

    return f'<html><body>{ranking_str}</body></html>'


@app.route('/')
def home_page():
    dynamo = boto3.resource('dynamodb', region_name='ca-central-1')
    scores_table = dynamo.Table('ddga_player_scores')

    course_scores = _group_scores_per_course(_read_all_scores(scores_table))
    _trim_scores(course_scores)
    
    return render_template('views/scores_table.html', ranked_player_scores=_get_rankings(course_scores))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
