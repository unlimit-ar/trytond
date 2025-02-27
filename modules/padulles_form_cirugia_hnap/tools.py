from dateutil.relativedelta import relativedelta
from datetime import datetime
from trytond.i18n import gettext


def compute_age_from_dates(dob):
    """ Get the person's age.
    """
    today = datetime.today().date()

    if dob:
        start = datetime.strptime(str(dob), '%Y-%m-%d')
        end = datetime.strptime(str(today), '%Y-%m-%d')

        rdelta = relativedelta(end, start)

        years_months_days = format_years_months_days(
            years=rdelta.years,
            months=rdelta.months,
            days=rdelta.days)
    
        return years_months_days

    return None


def format_years_months_days(years=None, months=None, days=None):
    year_str = gettext('form_cirugia_hnap.msg_compute_age_from_dates_year_str')
    month_str = gettext('form_cirugia_hnap.msg_compute_age_from_dates_month_str')
    day_str = gettext('form_cirugia_hnap.msg_compute_age_from_dates_day_str')

    ymd_format = '{years}{sep}{year_str}{sep} ' \
                 '{months}{sep}{month_str}{sep} ' \
                 '{days}{sep}{day_str}{sep}'

    return ymd_format.format(
        sep='\u200b',  # Zero width space
        # Make sure output.split(sep)[0, 2, 4] = [years, months, days], 
        # and we use '\u200d' (zero width joiner) as placeholder.
        years=isinstance(years, int) and str(years) or '\u200d',
        year_str=isinstance(years, int) and year_str or '\u200d',
        months=isinstance(months, int) and str(months) or '\u200d',
        month_str=isinstance(months, int) and month_str or '\u200d',
        days=isinstance(days, int) and str(days) or '\u200d',
        day_str=isinstance(days, int) and day_str or '\u200d')
