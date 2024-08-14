from datetime import datetime, timedelta


def generate_date_intervals(
    interval_days,
    start_year=2008,
    end_date=datetime.now(),
):
    dates = []
    end_year = end_date.year

    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            # Skip months beyond the end date in the final year
            if year == end_year and month > end_date.month:
                break

            # Calculate the number of days in the current month
            if month == 12:
                days_in_month = (
                    datetime(year + 1, 1, 1) - datetime(year, month, 1)
                ).days
            else:
                days_in_month = (
                    datetime(year, month + 1, 1) - datetime(year, month, 1)
                ).days

            # Adjust the days in the month if it's the current month and year
            if year == end_date.year and month == end_date.month:
                days_in_month = end_date.day

            # Loop through the month in intervals of `interval_days`
            for day in range(1, days_in_month + 1, interval_days):
                start_date = datetime(year, month, day)
                # Ensure the end date does not exceed the month or the specified end date
                end_interval_date = min(
                    start_date + timedelta(days=interval_days - 1),
                    datetime(year, month, days_in_month) + timedelta(days=1),
                    end_date
                    + timedelta(days=1),  # Ensure we don't go beyond the end_date
                )

                # Format the dates as strings and add them to the list
                dates.append(
                    f"{start_date.strftime('%Y-%m-%d')}..{end_interval_date.strftime('%Y-%m-%d')}"
                )
    return dates
