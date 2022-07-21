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


def main(argv):
    prog = argv.pop(0)
    parser = argparse.ArgumentParser(prog, description='Simple program with local database to track work time',
                                     # formatter_class=argparse.ArgumentDefaultsHelpFormatter # includes the default by default
                                     )

    parser.add_argument('--auto-ehbal', required=False, action='store_false', default=True,
                        help='Automatic display of the extra hours balance (default: %(default)s)')
    parser.add_argument('--auto-ttco', required=False, action='store_false', default=True,
                        help='Automatic display time to clock out after clocking in or out (default: %(default)s)')
    parser.add_argument('-t', '--no-tabs-on-report', dest='no_tabs', required=False, action='store_false', default=True,
                        help='Remove tabs from string reports (default: %(default)s)')
    parser.add_argument('--dont-check-errors', dest='check_errors', required=False, action='store_false', default=True,
                        help='Check for errors on time cards, if present, print a warn report (default: False)')

    subparsers = parser.add_subparsers(dest='cmd', help='sub-commands help')
    clock_parser = subparsers.add_parser('clock', help='Clocks in or out from work')
    ttco_parser = subparsers.add_parser('ttco', help='Show time to clock out')
    ehbal_parser = subparsers.add_parser('ehbal', help='Shows the extra hours balance')
    stc_parser = subparsers.add_parser('stc', help='Show time cards for a given day')
    stc_parser.add_argument('stc_date', type=str, nargs='?', default='Today',
                            help='The date to show time cards. Format: dd/mm/YYYY (default: %(default)s)',
                            metavar='DATE')
    rmtc_parser = subparsers.add_parser('rmtc', help='Deletes a time card using its uuid')
    rmtc_parser.add_argument('rmtc_uuid', type=str, help='The uuid of a time card to delete', metavar='UUID')
    addtc_parser = subparsers.add_parser('addtc', help='Creates a time card manually')
    addtc_parser.add_argument('addtc_datetime', nargs=2, type=str,
                              help='The datetime of the time card. Format: dd/mm/YYYY HH:MM:SS', metavar='DATETIME')
    addholi_parser = subparsers.add_parser('addholi', help='Inserts a holiday')
    addabs_parser = subparsers.add_parser('addabs', help='Justifies an absence')
    wdr_parser = subparsers.add_parser('wdr',
                                       help='Shows the work day report for a given status level (None ,"OK", "INFO", "WARN", "ERROR")')
    wdr_parser.add_argument('wdr_filter', type=str, nargs='?', default='OK',
                            help='Filter out work day reports with severity equal or below the given one. (default: %(default)s)',
                            metavar='FILTER')
    auto_clock_out_parser = subparsers.add_parser('coreg',
                                                  help='Clocks out from work on regular shift time')
    auto_clock_out_early_parser = subparsers.add_parser('coearly',
                                                        help='Clocks out from work earlier, regular shift minus launch Ïtime')

    args = parser.parse_args(argv)

    if args.cmd is None:
        parser.print_help(sys.stdout)
    else:
        cmd = args.cmd.lower()

        if cmd != 'wdr' and args.check_errors:
            time_card_service.print_work_day_status_report_if_recent_error(get_current_profile())

        if cmd == 'clock':
            time_card_service.clock_in_out(get_current_profile())
            if args.auto_ttco:
                print('---')
                time_card_service.print_today_report(get_current_profile(), from_auto_run=True, tabs=not args.no_tabs)
        elif cmd == 'ttco':
            time_card_service.print_today_report(get_current_profile(), tabs=not args.no_tabs)
        elif cmd == 'ehbal':
            time_card_service.print_extra_hours_balance_in_minutes(get_current_profile(), details=True)
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
        elif cmd == 'wdr':
            time_card_service.print_work_day_status_report(get_current_profile(), args.wdr_filter)
        elif cmd == 'coreg':
            time_card_service.clock_out_automatically(get_current_profile())
        elif cmd == 'coearly':
            time_card_service.clock_out_automatically(get_current_profile(), clock_early=True)

        if args.auto_ehbal and cmd != 'ehbal':
            print('---')
            time_card_service.print_extra_hours_balance_in_minutes(get_current_profile())


if __name__ == '__main__':
    try:
        main(sys.argv)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)
