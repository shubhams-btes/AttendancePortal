from datetime import date

WEEKEND_DAYS = [5, 6]


def is_holiday(check_date=None):

    if check_date is None:

        check_date = date.today()

    return check_date.weekday() in WEEKEND_DAYS