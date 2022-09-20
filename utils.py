import datetime


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
