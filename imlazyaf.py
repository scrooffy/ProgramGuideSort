"""  
    I'm lazy af script
    Basic script for automate editing the program guide
  
    by Ilya Kositsin

    Special for "Призыв" newspaper
    tnx to StackOverflow gentlemen and my laziness 
"""

__author__ = 'Ilya Kositsin'
__licence__ = 'MIT'
__version__ = '2.0.4'
__email__ = 'kositsin2010@yandex.ru'
__status__ = 'Production'

import os
import time
import argparse
from itertools import groupby
from collections import deque


def delete_markers(show: str) -> str:
    if not hasattr(delete_consecutive_identical_shows, 'useless_markers'):
        delete_markers.useless_markers = load_optimizing_filter('useless_markers')

    for marker in delete_markers.useless_markers:
        if marker in show:
            return show.replace(marker + ' ', '')

    return show


def replace_shows_with_names_of_series(show: str) -> str:
    if not hasattr(replace_shows_with_names_of_series, 'shows_with_names_of_series'):
        replace_shows_with_names_of_series.shows_with_names_of_series = load_optimizing_filter(
            'shows_with_names_of_series')

    for show_wnos in replace_shows_with_names_of_series.shows_with_names_of_series:
        if show_wnos in show:
            splt = show.split('"')
            splt[1] = show_wnos

            return str.join('"', splt)

    return show


def delete_consecutive_identical_shows(program_guide: list) -> list:
    previous_show = ''
    edited_program_guide = []

    for line in program_guide:
        time, show = line.split(maxsplit=1)
        show = replace_shows_with_names_of_series(delete_markers(show))

        if show != previous_show:
            edited_program_guide.append(time + ' ' + show)
        previous_show = show

    return edited_program_guide


def optimize_program_guide(chan_day_program: list, program_guide_pages_count: int) -> list:
    optimized_guide = []

    if not hasattr(optimize_program_guide, 'replacement_rules'):
        optimize_program_guide.replacement_rules = load_guide_filter()

    chan_day_program = delete_consecutive_identical_shows(delete_midnight_shows(chan_day_program))

    shows_list = {}
    for line in chan_day_program:
        time, show = line.split(maxsplit=1)

        for rule in list(optimize_program_guide.replacement_rules.keys()):
            if show == rule:
                show = optimize_program_guide.replacement_rules[rule]

        if show in shows_list.keys():
            shows_list[show].append(time)
        else:
            shows_list[show] = [time]

    for show in list(shows_list.keys()):
        line = ''
        for time in range(len(shows_list[show])):
            if time < len(shows_list[show]) - 1:
                line += shows_list[show][time] + ', '
            else:
                line += shows_list[show][time] + ' '
        line += show

        optimized_guide.append(line)

    if program_guide_pages_count == 2:
        optimized_guide.append('\n')

    return optimized_guide


def delete_midnight_shows(chan_day_program: list) -> list:
    unhappy_hours = ['01', '02', '03', '04', '05', '06', '07', '08']

    edited_guide = chan_day_program[0:int(len(chan_day_program) / 2)]
    unedited_part = chan_day_program[int(len(chan_day_program) / 2):len(chan_day_program)]

    for line in unedited_part:
        suspicious_hour = line.split('.')[0]

        is_midnight_show = False
        for bad_hour in unhappy_hours:
            if suspicious_hour == bad_hour:
                is_midnight_show = True

        if not is_midnight_show:
            edited_guide.append(line)

    return edited_guide


def day_sort_guide(program_guide_pages_count: int, _guide: list, chans_name: list, weekdays: list) -> list:
    _guide = [deque(i) for i in _guide]
    sorted_guide = [[] for i in range(len(weekdays))]

    chan_name_index = 0
    for _chan in _guide:
        _chan.popleft()
        _chan.popleft()
        _chan = list(filter('\n'.__ne__, _chan))

        chan_day_sort = [list(y) for x, y in groupby(_chan, lambda z: day_check(z, weekdays)) if not x]
        chan_day_sort = [optimize_program_guide(i, program_guide_pages_count) for i in chan_day_sort]

        for x in chan_day_sort:
            x.insert(0, chans_name[chan_name_index] + '\n')
        chan_name_index += 1

        sorted_guide = [i + j for i, j in zip(sorted_guide, chan_day_sort)]

    for i in range(len(sorted_guide)):
        sorted_guide[i].pop()
        sorted_guide[i][-1] = sorted_guide[i][-1].strip()

    return sorted_guide


def day_check(line: str, weekdays: list) -> bool:
    for day in weekdays:
        if line.startswith(day):
            return True

    return False


def load_guide(_chans: list) -> list:
    _guide = []
    for _chan in _chans:
        with open(os.path.join('in', _chan + '.txt'), 'r', encoding='windows-1251') as f:
            _guide.append(f.readlines())

    return _guide


def save_guide(_guide: list, _weekdays: list):
    dir_name = 'out'

    try:
        os.mkdir(dir_name)
    except FileExistsError:
        pass

    for i in range(len(_weekdays)):
        with open(os.path.join(dir_name, str(i + 1) + ' - ' + _weekdays[i] + '.txt'), 'w', encoding='utf-8') as f:
            f.writelines(_guide[i])


def load_chans_list(program_guide_pages_count: int) -> dict:
    chans = dict()
    buffer = []
    with open(os.path.join('settings', 'whitelist.txt'), 'r', encoding='utf-8-sig') as f:
        buffer = f.readlines()

    if program_guide_pages_count == 1:
        buffer = buffer[:-1]

    for i in buffer:
        chan_name_and_path = i.split(';', maxsplit=1)

        if '\\n' in chan_name_and_path[0]:
            chan_name_and_path[0] = chan_name_and_path[0].replace('\\n', '\n')

        chans[chan_name_and_path[0]] = chan_name_and_path[1].strip()

    return chans


def load_guide_filter() -> dict:
    filtr = dict()
    buffer = []
    with open(os.path.join('settings', 'filter.txt'), 'r', encoding='utf-8-sig') as f:
        buffer = f.readlines()

    for i in buffer:
        replacement_rule = i.split(';', maxsplit=1)

        if not replacement_rule[1].endswith('\n'):
            replacement_rule[1] += '\n'

        filtr[replacement_rule[0] + '\n'] = replacement_rule[1]

    return filtr


def load_optimizing_filter(name: str) -> list:
    filtr = list()
    with open(os.path.join('settings', name + '.txt'), 'r', encoding='utf-8') as f:
        for line in f:
            filtr.append(line.strip())

    return filtr


if __name__ == "__main__":
    start = time.perf_counter()

    parser = argparse.ArgumentParser()
    parser.add_argument('--pages', action='store', dest='count_of_pages_of_program_guide', type=int,
                        help='Count of pages of program guide (1 or 2)')
    args = parser.parse_args()
    if args.count_of_pages_of_program_guide != 1:
        args.count_of_pages_of_program_guide = 2

    chans = load_chans_list(args.count_of_pages_of_program_guide)

    weekdays = [
        'Понедельник',
        'Вторник',
        'Среда',
        'Четверг',
        'Пятница',
        'Суббота',
        'Воскресенье'
    ]

    guide = day_sort_guide(args.count_of_pages_of_program_guide, load_guide(list(chans.values())),
                           chans_name=list(chans.keys()), weekdays=weekdays)
    save_guide(guide, weekdays)

    print(f"Вместо 1.5 часа ты потратил {time.perf_counter() - start:0.4f} секунд")
