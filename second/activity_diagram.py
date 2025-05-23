import sqlite3
import datetime
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# German weekdays (abbreviated)
WEEKDAYS_DE = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']

DB_NAME = 'activity.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS activity (
        date TEXT PRIMARY KEY,
        count REAL DEFAULT 0
    )''')
    conn.commit()
    conn.close()

def set_activity(date_str, count):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('REPLACE INTO activity (date, count) VALUES (?, ?)', (date_str, count))
    conn.commit()
    conn.close()

def get_activity(date_str):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT count FROM activity WHERE date = ?', (date_str,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

def get_all_activities():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT date, count FROM activity ORDER BY date ASC')
    rows = c.fetchall()
    conn.close()
    return rows

def get_box_color(val, weekday):
    # Weekdays: 0-4 (Mo-Fr), Weekend: 5-6 (Sa-So)
    if weekday < 5:
        if val >= 10:
            # Brightest green
            return (50, 255, 50)
        else:
            # Grey for 0
            return (200, 200, 200)
    else:
        if val >= 3:
            # Brightest green for >=3 on weekend
            return (50, 255, 50)
        else:
            # Grey for 0
            return (200, 200, 200)

def get_activity_matrix(year):
    # Returns a 7 x 53 matrix (weekdays x weeks)
    first_day = datetime.date(year, 1, 1)
    last_day = datetime.date(year, 12, 31)
    matrix = np.zeros((7, 53), dtype=float)
    day = first_day
    prev_val = 0
    while day <= last_day:
        week = day.isocalendar()[1] - 1
        weekday = day.weekday()
        count = get_activity(day.isoformat())
        # Get previous day's value
        prev_day = day - datetime.timedelta(days=1)
        prev_val = get_activity(prev_day.isoformat()) if prev_day >= first_day else 0
        # Apply bonus if previous day was high
        if weekday < 5 and prev_val > 10:
            prev_val -= 10
            count += prev_val * (5/7)
        elif weekday >= 5 and prev_val > 3:
            prev_val -= 3
            count += prev_val * (5/7)
        matrix[weekday, week] = count
        day += datetime.timedelta(days=1)
    return matrix

def plot_activity(year):
    matrix = get_activity_matrix(year)
    cell_size = 20
    margin_left = 30
    margin_top = 0  # Removed top padding
    weekday_padding = 2  # Reduce this value to shrink the gap
    box_offset = 0  # Set to 0 for no extra gap
    width = margin_left + cell_size * matrix.shape[1]
    height = margin_top + cell_size * matrix.shape[0]
    img = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    # Draw weekdays
    font = None
    try:
        font = ImageFont.truetype('DejaVuSans.ttf', 14)
    except:
        font = ImageFont.load_default()
    for i, day in enumerate(WEEKDAYS_DE):
        draw.text((5, margin_top + i * cell_size + weekday_padding), day, fill='black', font=font)
    # Draw cells
    for y in range(matrix.shape[0]):
        for x in range(matrix.shape[1]):
            val = matrix[y, x]
            color = get_box_color(val, y)
            draw.rectangle([
                (margin_left + x * cell_size, margin_top + y * cell_size + box_offset),
                (margin_left + (x + 1) * cell_size - 2, margin_top + (y + 1) * cell_size - 2 + box_offset)
            ], fill=color, outline='gray')
    img.save(f'activity_{year}.png')
    print(f'Bild gespeichert als activity_{year}.png')

def edit_activity_for_day(date_str, new_count):
    set_activity(date_str, new_count)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='GitHub-like Activity Diagram with SQLite')
    parser.add_argument('--year', type=int, default=datetime.date.today().year, help='Jahr für das Diagramm')
    parser.add_argument('--set', nargs=2, metavar=('DATE', 'COUNT'), help='Setze Aktivität für ein Datum (YYYY-MM-DD COUNT)')
    parser.add_argument('--get', metavar='DATE', help='Hole Aktivität für ein Datum (YYYY-MM-DD)')
    args = parser.parse_args()

    init_db()

    if args.set:
        date_str, count = args.set
        set_activity(date_str, int(count))
        print(f'Aktivität für {date_str} gesetzt auf {count}')
    elif args.get:
        count = get_activity(args.get)
        print(f'Aktivität am {args.get}: {count}')
    else:
        plot_activity(args.year)
