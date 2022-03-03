import argparse
import datetime
import json
import os
import config


def main():
    parser = argparse.ArgumentParser('parser')
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
        print(f'Date: {date}')
        try:
            entries = os.listdir(date)
        except FileNotFoundError:
            print(f'{date} folder was not found.')
            continue

        for entry_path in entries:

            receive_code = entry_path.split('_')[-1]
            if receive_code not in config.CODES_TO_RESEND:
                continue
            print(f'{entry_path}:')
            for file_path in os.listdir(f'{date}/{entry_path}'):
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
                try:
                    if receive_code == '500':
                        error = json_log['error_data'].split('\n')[1]
                    else:
                        error = json_log['error_data']['detail']
                except:
                    error = ''
                print(f'-{file_path} {error}')


if __name__ == '__main__':
    main()
