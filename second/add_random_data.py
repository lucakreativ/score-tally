import random
import datetime
from activity_diagram import set_activity, init_db

# Add random data for a given year
def add_random_data(year, min_val=0, max_val=10):
    init_db()
    first_day = datetime.date(year, 1, 1)
    last_day = datetime.date(year, 12, 31)
    day = first_day
    while day <= last_day:
        count = random.randint(min_val, max_val)
        set_activity(day.isoformat(), count)
        day += datetime.timedelta(days=1)
    print(f"Random data for {year} added.")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Add random activity data for a year')
    parser.add_argument('--year', type=int, default=datetime.date.today().year, help='Year to fill with random data')
    parser.add_argument('--min', type=int, default=0, help='Minimum activity value')
    parser.add_argument('--max', type=int, default=10, help='Maximum activity value')
    args = parser.parse_args()
    add_random_data(args.year, args.min, args.max)
