from datetime import datetime


def time_func(func):
    def wrapper():
        start = datetime.now()
        func()
        end = datetime.now()
        delta = end-start
        print(f'{func}, finished in {delta}')
    return wrapper

def get_season_week(start: datetime = datetime(2019, 8, 24),
                    date:  datetime = datetime.now(),
                    end:   datetime = datetime(2020, 1, 11)) -> tuple:
    #handle the long as fuck first week
    if datetime(2019, 8, 18) <= date <= datetime(2019, 9, 2):
        return (date.year, 1)

    if start <= date <= end:
        total_weeks = (end - start).days//7
        return start.year, (total_weeks - (end - date).days//7)
    else:
        print(f'{date} not in range {start} - {end}')
        return (date.year, 1)