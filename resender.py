import argparse
import datetime
import requests
import json
import os
import config

def main():
    counter = 0
    counter_success = 0
    changes = []

    parser = argparse.ArgumentParser('parser')
    parser.add_argument('delete', type=int, help='Available types: 0 - Without delete 1 - With delete')
    parser.add_argument('date', type=str, help='"current" - current day | '
                                               '"01.01.2022" - exact date |'
                                               '"01.01.2022-03.02.2022" - period')

    args = parser.parse_args()
    if args.date == 'current':
        dates = [datetime.datetime.now().strftime('%d.%m.%Y')]
    elif '-' in args.date:
        start_date = datetime.datetime.strptime(args.date.split('-')[0], '%d.%m.%Y')
        end_date = datetime.datetime.strptime(args.date.split('-')[1], '%d.%m.%Y')
        days = [start_date + datetime.timedelta(days=i) for i in range((end_date-start_date).days + 1)]
        dates = [x.strftime('%d.%m.%Y') for x in days]
    else:
        dates = [args.date]

    print(f'Selected dates: {dates}')

    for date in dates:
        try:
            entries = os.listdir(date)
        except FileNotFoundError:
            print(f'{date} folder was not found.')
            continue

        for entry_path in entries:

            receive_code = entry_path.split('_')[-1]
            if receive_code not in config.CODES_TO_RESEND:
                continue

            for file_path in os.listdir(f'{date}/{entry_path}'):
                counter += 1
                with open(f'{date}/{entry_path}/{file_path}', 'r+') as f:
                    try:
                        json_log = json.load(f)
                    except:
                        continue
                try:
                    if json_log.get('uri').split('v1')[1] not in config.URLS_TO_RESEND:
                        continue
                except:
                    continue

                response = requests.post(
                    json_log.get('uri'),
                    data=json.dumps(json_log.get('data')),
                    headers={'content-type': 'application/json'},
                    verify=False)
                if response.status_code in [200, 201]:
                    counter_success += 1
                    changes.append(f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M")} '
                                   f'{date}/{entry_path}/{file_path} successfully resent')
                    if args.delete == 1:
                        changes[-1] += ' and was deleted.'
                        os.remove(f'{date}/{entry_path}/{file_path}')

                if response.status_code == 406:
                    changes.append(f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M")} '
                                   f'{date}/{entry_path}/{file_path} returned 406')
                    if args.delete == 1:
                        changes[-1] += ' and was deleted.'
                        os.remove(f'{date}/{entry_path}/{file_path}')

                print(f'[{counter_success}/{counter} ] {date} {entry_path} {file_path}{response.status_code}')

    with open(f'resender_logs.txt', 'a+') as f:
        f.writelines(line + '\n' for line in changes)


if __name__ == '__main__':
    main()
