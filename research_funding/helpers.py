import datetime

def age_from_birth_date(birth_date):
    today = datetime.date.today()
    years = today.year - birth_date.year
    if (today.month < birth_date.month or
        today.month == birth_date.month and today.day < birth_date.day):
       years = years - 1
    return years
