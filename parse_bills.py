import csv
import os
import json

DATA_ROOT = 'data'
BILL_TYPES = ['hr', 's', 'hjres', 'sjres']
BILLS_COLUMNS = [
    'billID',
    'active',
    'enacted',
    'vetoed',
    'officialTitle',
    'popularTitle'
]
SPONSORS_COLUMNS_USING_THOMAS = [
    'billID',
    'thomasID',
    'cosponsor'
]
SPONSORS_COLUMNS_USING_BIOGUIDE = [
    'billID',
    'bioguideID',
    'cosponsor'
]

subjects = set()
congresses = set()

bills_file = open('outputs/bills.csv', 'w')
bill_writer = csv.DictWriter(bills_file, BILLS_COLUMNS, extrasaction='ignore')
bill_writer.writeheader()

historical_sponsors_file = open('outputs/sponsors-historical.csv', 'w')
historical_sponsor_writer = csv.DictWriter(historical_sponsors_file, SPONSORS_COLUMNS_USING_THOMAS, extrasaction='ignore')
historical_sponsor_writer.writeheader()

current_sponsors_file = open('outputs/sponsors-current.csv', 'w')
current_sponsor_writer = csv.DictWriter(current_sponsors_file, SPONSORS_COLUMNS_USING_BIOGUIDE, extrasaction='ignore')
current_sponsor_writer.writeheader()

bill_subjects_file = open('outputs/bill_subjects.csv', 'w')
bill_subject_writer = csv.DictWriter(bill_subjects_file, ['billID', 'title'], extrasaction='ignore')
bill_subject_writer.writeheader()

bill_congresses_file = open('outputs/bill_congresses.csv', 'w')
bill_congress_writer = csv.DictWriter(bill_congresses_file, ['billID', 'number'], extrasaction='ignore')
bill_congress_writer.writeheader()

bill_committees_file = open('outputs/bill_committees.csv', 'w')
bill_committees_writer = csv.DictWriter(bill_committees_file, ['billID', 'committeeID'], extrasaction='ignore')
bill_committees_writer.writeheader()

for bill_type in BILL_TYPES:
    bill_records = []
    congresses_dir = os.path.join(DATA_ROOT, 'congress')
    for congress in os.listdir(congresses_dir):
        # We'll identify legislators using thomas_id for Congresses < 114th,
        # bioguide_id for Congresses >= 114th
        # https://github.com/legis-graph/legis-graph/issues/15
        congress_as_int = int(congress)
        if congress_as_int < 114:
            source_legislator_id = 'thomas_id'
            target_legislator_id = 'thomasID'
        else:
            source_legislator_id = 'bioguide_id'
            target_legislator_id = 'bioguideID'

        bills_dir = os.path.join(congresses_dir, congress, 'bills', bill_type)
        for bill_num in os.listdir(bills_dir):
            data_path = os.path.join(bills_dir, bill_num)
            bill_file = open(os.path.join(data_path, 'data.json'), 'r')
            bill_data = json.load(bill_file)

            # Write out the bill info
            bill_record = {}
            bill_record['billID'] = bill_data['bill_id']
            bill_record['active'] = bill_data['history']['active']
            bill_record['enacted'] = bill_data['history']['enacted']
            bill_record['vetoed'] = bill_data['history']['vetoed']
            bill_record['officialTitle'] = bill_data['official_title']
            bill_record['popularTitle'] = bill_data['popular_title']

            bill_writer.writerow(bill_record)

            # Write out the bill->sponsors relationships for this bill.
            for cosponsor in bill_data['cosponsors']:
                cosponsor_row = {
                    'billID': bill_data['bill_id'],
                    target_legislator_id: cosponsor[source_legislator_id],
                    'cosponsor': 1
                }
                if congress_as_int < 114:
                    historical_sponsor_writer.writerow(cosponsor_row)
                else:
                    current_sponsor_writer.writerow(cosponsor_row)

            sponsor = bill_data['sponsor']
            sponsor_row = {
                'billID': bill_data['bill_id'],
                target_legislator_id: sponsor[source_legislator_id],
                'cosponsor': 0
            }
            if congress_as_int < 114:
                historical_sponsor_writer.writerow(sponsor_row)
            else:
                current_sponsor_writer.writerow(sponsor_row)

            # Write out the bill-[:REFERRED_TO]->committee relationships for this bill
            for committee in bill_data['committees']:
                if committee['activity'] and len(committee['activity']) > 0 and committee['activity'][0] == 'referral':
                    record = {
                        'billID': bill_data['bill_id'],
                        'committeeID': committee['committee_id']
                    }
                    bill_committees_writer.writerow(record)

            # Write out the bill->subjects relationships and record the unique
            # subjects
            for subject in bill_data['subjects']:
                subjects.add(subject)
                bill_subject_writer.writerow({
                    'billID': bill_data['bill_id'],
                    'title': subject
                })

            # Write out the bill->congress relationship
            congresses.add(congress)
            bill_congress_writer.writerow({
                'number': congress,
                'billID': bill_data['bill_id']
            })

            bill_file.close()

bills_file.close()
historical_sponsors_file.close()
current_sponsors_file.close()
bill_congresses_file.close()
bill_subjects_file.close()
bill_committees_file.close()

# List of subjects
subjects_file = open('outputs/subjects.csv', 'w')
subject_writer = csv.DictWriter(subjects_file, ['title'], extrasaction='ignore')
subject_writer.writeheader()
for subject in subjects:
    subject_writer.writerow({'title': subject})
subjects_file.close()

# List of congresses
congresses_file = open('outputs/congresses.csv', 'w')
congress_writer = csv.DictWriter(congresses_file, ['number'], extrasaction='ignore')
congress_writer.writeheader()
for congress in congresses:
    congress_writer.writerow({'number': congress})
congresses_file.close()
