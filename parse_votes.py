import csv
import json
import os

HOUSE_VOTE_FIELDS  = [ 'bioguideID', 'billID', 'vote' ]
SENATE_VOTE_FIELDS = [ 'lisID', 'billID', 'vote' ]

house_votes_file = open('outputs/votes-house.csv', 'w')
house_vote_writer = csv.DictWriter(house_votes_file, HOUSE_VOTE_FIELDS, extrasaction='ignore')
house_vote_writer.writeheader()

senate_votes_file = open('outputs/votes-senate.csv', 'w')
senate_vote_writer = csv.DictWriter(senate_votes_file, SENATE_VOTE_FIELDS, extrasaction='ignore')
senate_vote_writer.writeheader()

congresses_dir = 'data/congress'
for congress in os.listdir(congresses_dir):
    congress_dir = os.path.join(congresses_dir, congress, 'votes')
    for year in os.listdir(congress_dir):
        year_dir = os.path.join(congress_dir, year)
        for vote in os.listdir(year_dir):
            vote_dir = os.path.join(year_dir, vote)
            vote_data_file = open(os.path.join(vote_dir, 'data.json'), 'r')
            vote_data = json.load(vote_data_file)

            # For now we only consider votes on bill passage and ignore the rest.
            if vote_data['category'] != 'passage':
                continue

            bill_id = '{}{}-{}'.format(vote_data['bill']['type'],
                    vote_data['bill']['number'], vote_data['bill']['congress'])

            # Legislators are indexed by bioguideID for House votes and
            # lisID for Senate votes:
            # https://github.com/legis-graph/legis-graph/issues/21
            if vote_data['chamber'] == 'h':
                target_legislator_id = 'bioguideID'
            else:
                target_legislator_id = 'lisID'

            for vote_type in vote_data['votes']:
                for voter in vote_data['votes'][vote_type]:
                    vote_row = {
                        target_legislator_id: voter['id'],
                        'billID': bill_id,
                        'vote': vote_type
                    }

                    if vote_data['chamber'] == 'h':
                        house_vote_writer.writerow(vote_row)
                    else:
                        senate_vote_writer.writerow(vote_row)

            vote_data_file.close()

house_votes_file.close()
senate_votes_file.close()
