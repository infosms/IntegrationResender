import datetime
import json
import os
import config
import requests

from aiogram import Bot, Dispatcher, executor, types

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot)


def get_dates(args_date):
    if args_date == 'current':
        return [datetime.datetime.now().strftime('%d.%m.%Y')]
    elif '-' in args_date:
        start_date = datetime.datetime.strptime(args_date.split('-')[0], '%d.%m.%Y')
        end_date = datetime.datetime.strptime(args_date.split('-')[1], '%d.%m.%Y')
        days = [start_date + datetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]
        return [x.strftime('%d.%m.%Y') for x in days]
    else:
        return [args_date]


@dp.message_handler(commands=['show_files'])
async def show_files(message: types.Message):
    dates = get_dates(message.get_args())
    msg = f'Выбранные даты: {dates}\n'

    for date in dates:
        msg += f'**Дата: {date}**\n'
        try:
            entries = os.listdir(f'{config.LOG_LOCATION}/{date}')
        except FileNotFoundError:
            msg += f'`Папка {date} пока не создана`\n'
            continue

        for entry_path in entries:
            receive_code = entry_path.split('_')[-1]

            if receive_code not in config.CODES_TO_RESEND:
                continue

            msg += f'{entry_path}: \n'
            for file_path in os.listdir(f'{config.LOG_LOCATION}/{date}/{entry_path}'):
                with open(f'{config.LOG_LOCATION}/{date}/{entry_path}/{file_path}', 'r+') as f:
                    try:
                        json_log = json.load(f)
                    except Exception as e:
                        msg += f'-{file_path} \n  `Не удалось открыть json: {e}`\n'
                        continue

                try:
                    url = json_log.get('uri').split('v1')[1]
                except Exception as e:
                    msg += f'-{file_path} \n  `Не удалось получить ссылку домена: {e}`\n'
                    continue

                if url not in config.URLS_TO_RESEND:
                    continue

                err_data = json_log.get('error_data')
                if not err_data:
                    msg += f'-{file_path} \n  `Не удалось получить причину ошибки`\n'
                    continue

                if receive_code == '500':
                    err_arr = json_log['error_data'].split('\n')
                    if len(err_arr) < 2:
                        msg += f'-{file_path} \n  `Не удалось получить причину ошибки 500`\n'
                        continue
                    msg += f'-{file_path} \n  {err_arr[1]}\n'
                else:
                    err_detail = err_data.get('detail')
                    if not err_detail:
                        msg += f'-{file_path} \n  `Не удалось получить причину ошибки`\n'
                        continue
                    msg += f'-{file_path} \n  {err_detail}\n'

    if len(msg) > 4096:
        for x in range(0, len(msg), 4096):
            await message.answer(msg[x:x + 4096], parse_mode='Markdown')
    else:
        await message.answer(msg, parse_mode='Markdown')


@dp.message_handler(commands=['resend'])
async def resend(message: types.Message):
    counter = 0
    counter_success = 0
    changes = []

    dates = get_dates(message.get_args())

    msg = f'Выбранные даты: {dates}\n'

    for date in dates:
        msg += f'*Дата: {date}\n*'
        try:
            entries = os.listdir(f'{config.LOG_LOCATION}/{date}')
        except FileNotFoundError:
            msg += f'`Папка {date} пока не создана`\n'
            continue

        for entry_path in entries:

            receive_code = entry_path.split('_')[-1]
            if receive_code not in config.CODES_TO_RESEND:
                continue

            for file_path in os.listdir(f'{config.LOG_LOCATION}/{date}/{entry_path}'):
                counter += 1

                prefix = f'[{counter_success}/{counter} ] {entry_path.replace("_", "")} {file_path} \n'

                with open(f'{config.LOG_LOCATION}/{date}/{entry_path}/{file_path}', 'r+') as f:
                    try:
                        json_log = json.load(f)
                    except Exception as e:
                        msg += f'{prefix} `Не удалось открыть json: {e}`\n'
                        continue

                try:
                    url = json_log.get('uri').split('v1')[1]
                except Exception as e:
                    msg += f'-{file_path} `Не удалось получить ссылку домена: {e}\n`'
                    continue

                if url not in config.URLS_TO_RESEND:
                    continue

                response = requests.post(
                    json_log.get('uri'),
                    data=json.dumps(json_log.get('data')),
                    headers={'content-type': 'application/json'},
                    verify=False
                )

                if response.status_code in [200, 201]:
                    counter_success += 1
                    changes.append(
                        f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M")} '
                        f'{config.LOG_LOCATION}/{date}/{entry_path}/{file_path} '
                        f'успешно переотправлен и удалён.'
                    )
                    os.remove(f'{config.LOG_LOCATION}/{date}/{entry_path}/{file_path}')
                    msg += f'{prefix} Успешно переотправлен\n'
                    continue

                if response.status_code in [500]:
                    resp_arr = response.text.split('\n')

                    if len(resp_arr) < 2:
                        msg += f'{prefix} {response.status_code} `{response.text}`'
                        continue
                    msg += f'{prefix} {response.status_code} `{" ".join(resp_arr[:2])}`'
                else:
                    try:
                        resp = json.loads(response.text)
                    except Exception as e:
                        msg += f'{prefix} {response.status_code} `Не удалось получить json ответа.`\n'
                        continue

                    resp_detail = resp.get('detail')
                    if not resp_detail:
                        msg += f'{prefix} {response.status_code} `Не удалось получить детальную причину.`\n'
                        continue

                    msg += f'{prefix} {response.status_code} `{resp_detail}` \n'

    with open(f'resender_logs.txt', 'a+') as f:
        f.writelines(line + '\n' for line in changes)

    if len(msg) > 4096:
        for x in range(0, len(msg), 4096):
            await message.answer(msg[x:x + 4096], parse_mode='Markdown')
    else:
        await message.answer(msg, parse_mode='Markdown')

if __name__ == '__main__':
    executor.start_polling(dp)
