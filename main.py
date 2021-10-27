#!/usr/bin/python3
# Copyright: (c) July, 25th, 2020
# Modified: July 23rd, 2021
# License: MIT
#
# A Script to simulate user interaction that will disable the screen
# from going to sleep and activating the Screen Saver.

__author__ = 'Virgil Hoover'
__version__ = '1.7.0'

# See change log for file versions and list of changes
import webbrowser as web
from argparse import ArgumentParser
from datetime import datetime as dt
from logging import getLogger
from logging.config import dictConfig
from msvcrt import getwche, kbhit
from os import getenv, system
from random import randint
from sys import exit, platform, stdout
from time import monotonic, sleep

from pyautogui import press
from yaml import safe_load


class TimeoutExpired(Exception):
    """
    A custom exception.
    """
    pass


def input_with_timeout(timeout: int, timer=monotonic) -> str:
    """
    Start a separate thread with a timer on a prompt
    for additional information.

    Args:
        timeout: an integer value to represent seconds.
        timer: a system clock to track time
    """
    stdout.write('Would you like to log disconnects? (Y/n) ')
    stdout.flush()
    endtime = timer() + timeout
    result = []
    while timer() < endtime:
        if kbhit():
            result.append(getwche())
            if result[-1] == '\r':
                return ''.join(result[:-1])
        sleep(0.02)
    raise TimeoutExpired


def check_disconnects() -> bool:
    """
    Prompt for additional logging information.

    :return: boolean value determining additional information
    """
    try:
        answer = input_with_timeout(5)
    except TimeoutExpired:
        return True
    else:
        return False


def log_level() -> tuple:
    """
    Check for command line arguments.
    """
    _parser = ArgumentParser(prog='main.py', add_help=True)
    _parser.add_argument('--debug', action='store_true',
                         help='Sets the debug log level to true',
                         required=False)
    _parser.add_argument('--password', metavar='passwd', nargs=1,
                         help='The password to proceed', required=False)
    args = _parser.parse_args()
    if args.password == getenv('sim_key'):
        if args.debug:
            return 'UserSimulation', 0
        else:
            return 'SysKey', 10
    else:
        return 'SysKey', 10


def user_simulation(name: str = 'SysKey', log_lvl: int = 10) -> tuple:
    """
    This function simulates a user input to disable the screen going
    to sleep, and / or activating a screen saver.

    :param name: The name used for the title of the window.
    :param log_lvl: integer to indicate the logging level
    :returns count: the number of intervals ran.
    :returns duration: the total running time of the app.
    """
    # Set color variables
    cyan = '\x1b[3;36;40m'
    red = '\x1b[3;31;40m'
    green = '\x1b[1;32;40m'
    yellow = '\x1b[2;33;40m'

    # Set some variables like window size, the key used, and a counter.
    system('mode con: cols=40 lines=6')
    simulation_key = 'shift'
    # simulation_key = 'scrolllock'
    key_pressed_counter = 0
    duration_total = 0
    start = dt.strptime('18:00', '%H:%M')
    stop = dt.strptime('06:00', '%H:%M')
    # Perform user input simulation to disable the screen going to sleep.
    try:
        if not time_in_range(dt.now(), start, stop):
            exit(0)
        while True:

            # Clear the screen and set window title, depending on the OS.
            if platform == 'win32':
                system('title ' + name)
            else:
                print('\33]0;' + name + '\a', end='')
            clear_screen()

            # Format console output with color.
            if log_lvl == 10:
                print('**-------DEBUG-------**\n')
            print(green + ' ** User Input Simulation **\n',
                  yellow + '** Press Ctrl + C to quit **')
            random_number = randint(1, 4) * 60
            duration_time = int(random_number / 60)
            press(simulation_key)
            key_pressed_counter += 1

            # Check if it is the iteration and give correct tense.
            correct_term = {1: 'time'}
            tense = correct_term.get(key_pressed_counter, 'times')
            print('', cyan + str(duration_time), red + 'minute interval\n',
                  cyan + simulation_key, red + 'has been pressed',
                  cyan + str(key_pressed_counter), red + tense)
            print('', red + 'For a total time of',
                  cyan + str(convert_time(duration_total)))
            duration_total += random_number
            countdown(random_number)

    except KeyboardInterrupt:
        # Listen for the user to actually press the key combo
        clear_screen()
        return str(convert_time(duration_total)), str(key_pressed_counter)


def clear_screen() -> None:
    """
    OS specific command to clear the terminal screen of text.
    """
    if platform == 'win32':
        system('cls')
    else:
        system('clear')


def convert_time(seconds: int) -> str:
    """
    Convert time from seconds to hours and minutes.

    Args:
        seconds: a positive number to be converted.
    """
    hours = (seconds % (24 * 3600)) // 3600
    seconds %= 3600
    minutes = seconds // 60
    return '{:02d}:{:02d}'.format(hours, minutes)


def countdown(t: int) -> None:
    """
    A countdown timer with formatting for each interval the
    application runs.

    Args:
        t: the starting time value for counting down.
    """
    while t:
        time_format = '\x1b[3;36;40m {:02d}:{:02d}\x1b[3;31;40m currently ' \
                      'remaining'.format(*divmod(t, 60))
        print(time_format, end='\r')
        sleep(1)
        t -= 1


def time_in_range(time_to_compare: dt, start_time: dt,
                  end_time: dt) -> bool:
    """
    Return true if x is in the range [start, end]
    where x is the time to compare.

    Args:
        time_to_compare: time time that must fall between start and
        end to return true.
        start_time: the minimum time value allowed.
        end_time: the maximum time value allowed.
    """
    if start_time <= end_time:
        return start_time <= time_to_compare <= end_time
    else:
        return start_time <= time_to_compare or time_to_compare <= end_time


def file_log(start: str, msg: str, lvl: str, disconnects: bool) -> None:
    """
    File logging for record keeping. Set the log level to Info, format the
    log entry capturing the entry time stamp, the logger, the start time, the
    difference, the disconnects, the timer value and the count of key presses.

    Args:
        start: the program start date and time in string format
        msg: the string placed in the log file with the time stamp.
        lvl: the logger to use for log entries.
        disconnects: boolean value indicating additional information to be
        logged.
    """
    final_str = ''
    __name__ = lvl
    with open('config.yaml', 'r') as f:
        dictConfig(safe_load(f.read()))

    logger = getLogger(__name__)

    # Calculate the time delta for the program run.
    _time_dif = dt.now() - dt.strptime(start, '%Y-%m-%d %H:%M:%S')
    final_str += start + ' | ' + str(_time_dif)[:str(_time_dif).find('.')]

    if disconnects:
        error_count = input('How many disconnects: ')
        error_count += ' disconnects | ' + msg
        final_str += ' | ' + error_count
    else:
        final_str += ' | 0 disconnects logged | ' + msg

    try:
        if lvl == 'UserSimulation':
            logger.debug(final_str, exc_info=True)
        elif lvl == 'SysKey':
            logger.info(final_str)
        elif lvl == 'pkg_check':
            logger.error(final_str, exc_info=True)
        sleep(1)
        web.open('time.log')
    except (IOError, OSError) as e:
        logger.exception('CRITICAL ERROR: ' + e + '\n', exc_info=True,
                         stack_info=True)


if __name__ == '__main__':
    time_start = dt.now().strftime('%Y-%m-%d %H:%M:%S')
    level, lvl_int = log_level()
    check_results = check_disconnects()
    duration, count = user_simulation(level, lvl_int)
    clear_screen()
    file_log(time_start, duration + ' | count: ' + count, level, check_results)
