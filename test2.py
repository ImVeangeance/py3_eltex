import sys
import sqlite3
import json

'''Args for better understanding time transfer function'''
MINUTE = 60
HOUR = 3600
DAY = 86400
WEEK = 604800


def create_table_nh(cursor: sqlite3.Cursor, rt: dict):
    cursor.execute("create table next_hop (next_hop text)")
    for next_hop in rt["route_table"]["next_hop"]:
        cursor.execute("insert into next_hop values (?)", (next_hop,))


def age_type_to_seconds(age):
    temp = age.split(' ')[-1].split(':')
    tempf = 0
    if len(age) > 8:
        temp_ = age.split(' ')[0].split('w')
        if len(temp_) > 1:
            tempf = int(temp_[1][:-1]) * DAY + int(temp_[0]) * WEEK
        else:
            tempf = int(temp_[-1][:-1]) * DAY
        age_sp = int(temp[-1]) + int(temp[-2]) * MINUTE + int(temp[-3]) * HOUR
    else:
        age_sp = int(temp[-1]) + int(temp[-2]) * MINUTE + int(temp[-3]) * HOUR
    return age_sp + tempf


def seconds_to_age_type(seconds_for_formatting):
    week: str = seconds_for_formatting // WEEK
    day: str = (seconds_for_formatting % WEEK) // DAY
    hour: str = ((seconds_for_formatting % WEEK) % DAY) // HOUR
    minute: str = (((seconds_for_formatting % WEEK) % DAY) % HOUR) // MINUTE
    seconds: str = (((seconds_for_formatting % WEEK) % DAY) % HOUR) % MINUTE
    if len(str(hour)) == 1:
        hour = '0' + str(hour)
    if len(str(minute)) == 1:
        minute = '0' + str(minute)
    if len(str(seconds)) == 1:
        seconds = '0' + str(seconds)
    return str(str(week) + 'w' + str(day) + "d " + str(hour) + ':' + str(minute) + ':' + str(seconds))


def create_table_destination(cursor: sqlite3.Cursor, rt: dict):
    cursor.execute("create table destination (destin text, prefer integer, "
                   "metric integer, next_hop text, interface text, age integer)")
    for next_hop, sec_dict in rt["route_table"]["next_hop"].items():
        for dest, data in sec_dict.items():
            cursor.execute("insert into destination values (?, ?, ?, ?, ?, ?)",
                           (dest, data["preference"], data["metric"], next_hop,
                            data["via"], age_type_to_seconds(data["age"])))


def print_table(cursor: sqlite3.Cursor):
    print("| Destination          | Prf | Metric | Next hop        | "
          "Interface     | Age")
    previous = None
    for rows in cursor.execute("select * from destination order by destin"):
        rows = list(rows)
        if rows[0] == previous:
            rows[0] = ''
        rows[-1] = seconds_to_age_type(rows[-1])
        print("| {:<18} | {:<3} | {:<6} | {:<15} | {:<13} | {}".format(*rows))
        previous = rows[0]


if "__main__" == __name__:
    try:
        input_file = open(sys.argv[1], 'r')
        output_file = sys.argv[-1]
        table = json.load(input_file)
        with sqlite3.connect(output_file) as connect:
            create_table_nh(connect.cursor(), table)
            create_table_destination(connect.cursor(), table)
        print_table(connect.cursor())
    except json.decoder.JSONDecodeError as e:
        print("JSON file has bad format ", e, file=sys.stderr)
    except sqlite3.OperationalError as e:
        print(e, file=sys.stderr)
    except IOError:
        print("Incorrect file name or file is not in the current directory!")
