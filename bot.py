import datetime
import json
import os
import config
import requests

from aiogram import Bot, Dispatcher, executor, types

# Launching
bot = Bot(token='5142923760:AAFB6oIm-hhBakUG1Jo1QinCKq1Nnw5miHQ')
dp = Dispatcher(bot)


@dp.message_handler(commands=['show_files'])
async def show_files(message: types.Message):
    args_date = message.get_args()
    if args_date == 'current':
        dates = [datetime.datetime.now().strftime('%d.%m.%Y')]
    elif '-' in args_date:
        start_date = datetime.datetime.strptime(args_date.split('-')[0], '%d.%m.%Y')
        end_date = datetime.datetime.strptime(args_date.split('-')[1], '%d.%m.%Y')
        days = [start_date + datetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]
        dates = [x.strftime('%d.%m.%Y') for x in days]
    else:
        dates = [args_date]

    msg = f'Выбранные даты: {dates}\n'

    for date in dates:
        msg += f'Дата: {date}\n'
        try:
            entries = os.listdir(date)
        except FileNotFoundError:
            msg += f'Папка {date} пока не создана\n'
            continue
        for entry_path in entries:
            receive_code = entry_path.split('_')[-1]
            if receive_code not in ['403', '500', '502', '503', '504']:
                continue
            msg += f'{entry_path}: \n'
            for file_path in os.listdir(f'{date}/{entry_path}'):
                with open(f'{date}/{entry_path}/{file_path}', 'r+') as f:
                    try:
                        json_log = json.load(f)
                    except:
                        continue
                try:
                    if receive_code == '500':
                        error = json_log['error_data'].split('\n')[1]
                    else:
                        error = json_log['error_data']['detail']
                except:
                    error = ''
                msg += f'-{file_path} {error} \n'
    if len(msg) > 4096:
        for x in range(0, len(msg), 4096):
            await message.answer(msg[x:x + 4096])
    else:
        await message.answer(msg)


@dp.message_handler(commands=['resend'])
async def resend(message: types.Message):
    counter = 0
    counter_success = 0
    changes = []

    args_date = message.get_args()
    if args_date == 'current':
        dates = [datetime.datetime.now().strftime('%d.%m.%Y')]
    elif '-' in args_date:
        start_date = datetime.datetime.strptime(args_date.split('-')[0], '%d.%m.%Y')
        end_date = datetime.datetime.strptime(args_date.split('-')[1], '%d.%m.%Y')
        days = [start_date + datetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]
        dates = [x.strftime('%d.%m.%Y') for x in days]
    else:
        dates = [args_date]

    msg = f'Выбранные даты: {dates}\n'

    for date in dates:
        msg += f'Дата: {date}\n'
        try:
            entries = os.listdir(date)
        except FileNotFoundError:
            msg += f'Папка {date} пока не создана\n'
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
                    changes[-1] += ' and was deleted.'
                    os.remove(f'{date}/{entry_path}/{file_path}')

                if response.status_code == 406:
                    changes.append(f'{datetime.datetime.now().strftime("%d.%m.%Y %H:%M")} '
                                   f'{date}/{entry_path}/{file_path} returned 406')
                    changes[-1] += ' and was deleted.'
                    os.remove(f'{date}/{entry_path}/{file_path}')

                msg += f'[{counter_success}/{counter} ] {date} {entry_path} {file_path}{response.status_code}\n'

    with open(f'resender_logs.txt', 'a+') as f:
        f.writelines(line + '\n' for line in changes)

    if len(msg) > 4096:
        for x in range(0, len(msg), 4096):
            await message.answer(msg[x:x + 4096])
    else:
        await message.answer(msg)

if __name__ == '__main__':
    executor.start_polling(dp)
