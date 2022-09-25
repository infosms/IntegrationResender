import argparse
import datetime
import requests
import json
import os
import config
import utils


def main():
    counter = 0
    counter_success = 0
    changes = []

    parser = argparse.ArgumentParser('parser')
    parser.add_argument('date', type=str)
    args = parser.parse_args()
    dates = utils.get_dates(args.date)

    print(f'Выбранные даты: {dates}\n')

    for date in dates:
        print(f'*Дата: {date}*\n')
        try:
            entries = os.listdir(f'{config.LOG_LOCATION}/{date}')
        except FileNotFoundError:
            print(f'`Папка {date} пока не создана`\n')
            continue

        for entry_path in entries:

            receive_code = entry_path.split('_')[-1]
            if receive_code not in config.CODES_TO_RESEND:
                continue

            for file_path in os.listdir(f'{config.LOG_LOCATION}/{date}/{entry_path}'):
                counter += 1

                prefix = f'[{counter_success}/{counter} ] {entry_path.replace("_", "")} {file_path}'

                with open(f'{config.LOG_LOCATION}/{date}/{entry_path}/{file_path}', 'r+') as f:
                    try:
                        json_log = json.load(f)
                    except Exception as e:
                        print(f'{prefix} \n `Не удалось открыть json: {e}`\n')
                        continue

                try:
                    url = json_log.get('uri').split('v1')[1]
                except Exception as e:
                    print(f'{prefix} \n `Не удалось получить ссылку домена: {e}`\n')
                    continue

                if url not in config.URLS_TO_RESEND:
                    continue

                try:
                    response = requests.post(
                        json_log.get('uri'),
                        data=json.dumps(json_log.get('data')),
                        headers={'content-type': 'application/json'},
                        verify=False
                    )
                except Exception as e:
                    print(f'{prefix} \n `Не удалось послать запрос: {e}\n`')
                    continue

                if response.status_code in [200, 201]:
                    counter_success += 1
                    changes.append(
                        f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M")} '
                        f'{config.LOG_LOCATION}/{date}/{entry_path}/{file_path} '
                        f'успешно переотправлен и удалён.'
                    )
                    os.remove(f'{config.LOG_LOCATION}/{date}/{entry_path}/{file_path}')
                    print(f'{prefix} Успешно переотправлен\n')
                    continue

                if response.status_code in [406]:
                    changes.append(
                        f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M")} '
                        f'{config.LOG_LOCATION}/{date}/{entry_path}/{file_path} '
                        f'был дубликатом и удалён.'
                    )
                    os.remove(f'{config.LOG_LOCATION}/{date}/{entry_path}/{file_path}')
                    print(f'{prefix} был дубликатом\n')
                    continue

                if response.status_code in [500]:
                    resp_arr = response.text.split('\n')

                    if len(resp_arr) < 2:
                        print(f'{prefix} \n {response.status_code} `{response.text}`\n')
                        continue
                    print(f'{prefix} \n {response.status_code} `{" ".join(resp_arr[:2])}`\n')
                else:
                    try:
                        resp = json.loads(response.text)
                    except Exception as e:
                        print(f'{prefix} \n {response.status_code} `Не удалось получить json ответа.`\n')
                        continue

                    resp_detail = resp.get('detail')
                    if not resp_detail:
                        print(f'{prefix} \n {response.status_code} `Не удалось получить детальную причину.`\n')
                        continue

                    print(f'{prefix} \n {response.status_code} `{resp_detail}` \n')

    with open(f'resender_logs.txt', 'a+') as f:
        f.writelines(line + '\n' for line in changes)


if __name__ == '__main__':
    main()
