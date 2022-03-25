import argparse
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from wtt.services import time_card as time_card_service
from wtt.services import profile as profile_service
from wtt.services import holiday as holiday_service
from wtt.services import absence as absence_service
from wtt.utils import date as date_utils


def get_current_profile():
    return profile_service.get_current_profile()


def get_error_report():
    # Error - odd number of points per day
    # Missing - No point for a work day (excluding holiday and absences)
    # Illegal - more than 8 + 2 hours per day, 6+ hours straight, no lunch time, lunch < 1, interval between days (<11)
    # Warning - work on holiday or weekend
    # OK
    pass  # TODO make a function to generate this report, this function can accept time filter, e.g. last 3 months


def main(argv):
    prog = argv.pop(0)
    parser = argparse.ArgumentParser(prog, description='Simple program with local database to track work time',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--auto-ehbal', required=False, action='store_false', default=True,
                        help='Automatic display of the extra hours balance')
    parser.add_argument('--auto-ttco', required=False, action='store_false', default=True,
                        help='Automatic display time to clock out after clocking in or out')

    subparsers = parser.add_subparsers(dest='cmd', help='sub-commands help')
    clock_parser = subparsers.add_parser('clock', help='Clocks in or out from work')
    ttco_parser = subparsers.add_parser('ttco', help='Show time to clock out')
    ehbal_parser = subparsers.add_parser('ehbal', help='Shows the extra hours balance')
    stc_parser = subparsers.add_parser('stc', help='Show time cards for a given day')
    stc_parser.add_argument('stc_date', type=str, nargs='?', default='Today',
                            help='The date to show time cards. Format: dd/mm/YYYY', metavar='DATE')
    rmtc_parser = subparsers.add_parser('rmtc', help='Deletes a time card using its uuid')
    rmtc_parser.add_argument('rmtc_uuid', type=str, help='The uuid of a time card to delete', metavar='UUID')
    addtc_parser = subparsers.add_parser('addtc', help='Creates a time card manually')
    addtc_parser.add_argument('addtc_datetime', nargs=2, type=str,
                              help='The datetime of the time card. Format: dd/mm/YYYY HH:MM:SS', metavar='DATETIME')
    addholi_parser = subparsers.add_parser('addholi', help='Inserts a holiday')
    addabs_parser = subparsers.add_parser('addabs', help='Justifies an absence')

    args = parser.parse_args(argv)

    if args.cmd is None:
        parser.print_help(sys.stdout)
    else:
        cmd = args.cmd.lower()
        if cmd == 'clock':
            time_card_service.clock_in_out(get_current_profile())
            if args.auto_ttco:
                print('---')
                time_card_service.print_today_report(get_current_profile())
        elif cmd == 'ttco':
            time_card_service.print_today_report(get_current_profile())
        elif cmd == 'ehbal':
            time_card_service.print_extra_hours_balance_in_minutes(get_current_profile())
        elif cmd == 'stc':
            if args.stc_date.lower() == 'today':
                date = date_utils.get_now()
            else:
                date = date_utils.string_to_datetime(args.stc_date)
            time_card_service.display_time_cards_of_a_day(get_current_profile(), date)
        elif cmd == 'rmtc':
            time_card_service.delete_time_card(get_current_profile(), args.rmtc_uuid)
        elif cmd == 'addtc':
            date = args.addtc_datetime
            if type(args.addtc_datetime) is list:
                date = ' '.join(args.addtc_datetime)
            time_card_service.clock_in_out_manually(get_current_profile(), date)
        elif cmd == 'addholi':
            holiday_service.prompt_and_insert_holiday()
        elif cmd == 'addabs':
            absence_service.prompt_and_insert_absence(get_current_profile())

        if args.auto_ehbal and cmd != 'ehbal':
            print('---')
            time_card_service.print_extra_hours_balance_in_minutes(get_current_profile())


if __name__ == '__main__':
    try:
        main(sys.argv)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)
