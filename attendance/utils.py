from datetime import date
from django.db.models import Q

from .models import Holiday

WEEKEND_DAYS = [5,6]   # Sunday only — adjust if you also close Saturdays


def _holiday_query(check_date, batch=None):
    """Holiday/OO rows covering check_date, global OR for this batch."""
    return Holiday.objects.filter(
        start_date__lte=check_date,
    ).filter(
        Q(end_date__gte=check_date) | Q(end_date__isnull=True, start_date=check_date)
    ).filter(
        Q(batch__isnull=True) | Q(batch=batch)
    )


def is_holiday(check_date=None, batch=None):
    """Boolean: is this a non-working day (weekend OR holiday OR batch OO)?
    Used to GATE attendance marking."""
    if check_date is None:
        check_date = date.today()

    if check_date.weekday() in WEEKEND_DAYS:
        return True

    return _holiday_query(check_date, batch).exists()


def holiday_type(check_date, batch=None):
    """What KIND of non-working day is this? Drives report display.
    Returns 'WEEKEND', 'OO', 'HOLIDAY', or None."""
    if check_date.weekday() in WEEKEND_DAYS:
        return "WEEKEND"

    hol = _holiday_query(check_date, batch).first()
    if hol:
        return hol.type   # "OO" or "HOLIDAY"

    return None