import boto3
import argparse
import uuid

from csv import DictReader


def read_score_sheet(score_sheet: str) -> list:
    scores = []
    
    with open(score_sheet, 'r') as score_sheet_csv:
        reader = DictReader(score_sheet_csv)
        
        for row in reader:
            if row.get('PlayerName', 'Par') == 'Par':
                continue
            row['ScoreID'] = f"{row['PlayerName']} {row['Date']}"
            
            scores.append(dict(row))
            print(f'Read Score: {row}')
    
    return scores


def write_scores_to_dynamo(dynamo: boto3.resource, scores: tuple):
    scores_table = dynamo.Table('ddga_player_scores')

    with scores_table.batch_writer() as batch:
        for score in scores:
            batch.put_item(Item=score)


def main(event, context):
    session = boto3.session.Session()
    dynamo = session.resource('dynamodb')

    scores = read_score_sheet(context)
    write_scores_to_dynamo(dynamo, scores)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("score_sheet", type=str)
    args = parser.parse_args()

    main({}, args.score_sheet)
