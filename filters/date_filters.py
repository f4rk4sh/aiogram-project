from datetime import date

week = {
    1: "Monday",
    2: "Tuesday",
    3: "Wednesday",
    4: "Thursday",
    5: "Friday",
    6: "Saturday",
    7: "Sunday"
}

months = {
    (2,): 28,
    (4, 6, 9, 11): 30,
    (1, 3, 5, 7, 8, 10, 12): 31
}

years = [2024, 2028, 2032, 2036, 2040]


def get_dates(day, today_date=None):
    if not today_date:
        today = date.today()
        s = []
        if day != 1:
            i = day
            day_today = today.day
            while i > 1:
                text = str(day_today - 1) + '.0' + str(today.month)
                s.insert(0, text)
                i -= 1
                day_today -= 1

        next_day = today.day
        for i in range(day, 8):
            text = str(next_day) + '.0' + str(today.month)
            s.append(text)
            next_day += 1
        return s


def update_dates(text=None, dates=None):
    this_year = date.today().year
    updated_dates = []
    number_of_days = 0
    if text == "Next week":
        last_date = dates[-1].split('.')
        last_day = int(last_date[0])
        month = int(last_date[1])
        last_day_in_next_month = 0
        for m in months.keys():
            if month in m and this_year not in years:
                number_of_days = months[m]
                break
            else:
                number_of_days = 29
        while len(updated_dates) < 7:
            if last_day + 1 <= number_of_days:
                updated_dates.append(f'{last_day + 1}.{last_date[1]}')
                last_day += 1
            else:
                last_day_in_next_month += 1
                if month < 10:
                    updated_dates.append(f'{last_day_in_next_month}.0{month + 1}')
                else:
                    updated_dates.append(f'{last_day_in_next_month}.{month + 1}')

    else:
        first_date = dates[0].split('.')
        first_day = int(first_date[0])
        month = int(first_date[1])
        i = 0
        while len(updated_dates) < 7:
            if first_day - 1 > 0:
                updated_dates.insert(0, f'{first_day - 1}.{first_date[1]}')
                first_day -= 1
            else:
                previous_month = month - 1
                for m in months.keys():
                    if previous_month in m and this_year not in years:
                        number_of_days = months[m]
                        break
                    else:
                        number_of_days = 29

                updated_first_day = number_of_days
                if month < 10:
                    updated_dates.insert(0, f'{updated_first_day - i}.0{previous_month}')
                else:
                    updated_dates.insert(0, f'{updated_first_day - i}.{previous_month}')
                i += 1
    return updated_dates
