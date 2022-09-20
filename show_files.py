import argparse
import json
import os
import config
import utils


def main():
    parser = argparse.ArgumentParser('parser')
    parser.add_argument('date', type=str)
    args = parser.parse_args()

    dates = utils.get_dates(args.date)

    print(f'Выбранные даты: {dates}')

    for date in dates:
        print(f'Дата: {date}\n')
        try:
            entries = os.listdir(f'{config.LOG_LOCATION}/{date}')
        except FileNotFoundError:
            print(f'`Папка {date} пока не создана`\n')
            continue

        for entry_path in entries:
            receive_code = entry_path.split('_')[-1]

            if receive_code not in config.CODES_TO_RESEND:
                continue

            print(f'{entry_path.replace("_", ".")}: \n')
            for file_path in os.listdir(f'{config.LOG_LOCATION}/{date}/{entry_path}'):
                with open(f'{config.LOG_LOCATION}/{date}/{entry_path}/{file_path}', 'r+') as f:
                    try:
                        json_log = json.load(f)
                    except Exception as e:
                        print(f'-{file_path} \n  `Не удалось открыть json: {e}`\n')
                        continue

                try:
                    url = json_log.get('uri').split('v1')[1]
                except Exception as e:
                    print(f'-{file_path} \n  `Не удалось получить ссылку домена: {e}`\n')
                    continue

                if url not in config.URLS_TO_RESEND:
                    continue

                err_data = json_log.get('error_data')
                if not err_data:
                    print(f'-{file_path} \n  `Не удалось получить причину ошибки`\n')
                    continue

                if receive_code == '500':
                    err_arr = json_log['error_data'].split('\n')
                    if len(err_arr) < 2:
                        print(f'-{file_path} \n  `Не удалось получить причину ошибки 500`\n')
                        continue
                    print(f'-{file_path} \n  `{err_arr[1]}`\n')
                else:
                    err_detail = err_data.get('detail')
                    if not err_detail:
                        print(f'-{file_path} \n  `Не удалось получить причину ошибки`\n')
                        continue
                    print(f'-{file_path} \n  `{err_detail}`\n')


if __name__ == '__main__':
    main()
