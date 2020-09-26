import click
import os
import datetime
from memory_profiler import profile

from seeker import get_all_employees, _normalize_datetime, get_total_work_time


def _get_list_file_selection():
    files: list = ['']
    n = 1

    for file in os.scandir('xml'):
        if file.name.endswith('.xml'):
            click.echo(f"[{n}] {click.style(file.name, fg='green')}")
            files.append(file)
            n += 1

    while True:
        n = click.prompt(text=f"Select number file",
                         type=click.IntRange(1, len(files) - 1))
        break

    return os.path.abspath(files[n].path)


def _get_selection_employee(path_to_file: str):
    select = click.confirm("Do you want to choose an employee's"
                           " name? otherwise, enter", default=False)

    employees = []

    if select:
        employees = get_all_employees(path_to_file)

        def generator_employees():
            for n in employees:
                yield f"{n}\n"

        click.echo_via_pager(generator_employees())

    while True:
        name = click.prompt("Enter name employee", type=str,
                            default='-').strip()

        if not select and name == '-':
            break

        if not employees:
            employees = get_all_employees(path_to_file)

        if name in employees:
            break
        else:
            click.echo(click.style("Select name not found!", fg='red'))

    return name


def _get_from_date():
    while True:
        date = click.prompt("Enter 'from' date on format"
                            " 'year-month-day hour:minute:sec'"
                            " or 'year-month-day'", default='')

        if date:
            try:
                _normalize_datetime(date)
                break
            except ValueError:
                click.secho('Wrong enter data!', fg='red')
                continue
        else:
            break

    return date


def _get_to_date(date_from):
    while True:
        date = click.prompt("Enter 'to' date on format"
                            " 'year-month-day hour:minute:sec'"
                            " or 'year-month-day'", default='')

        if date:
            try:
                _date = _normalize_datetime(date)

                if date_from:
                    _date_from = _normalize_datetime(date_from)

                    if _date_from >= _date:
                        click.secho('Date "to" cannot more or equal '
                                    'to "from" !', fg='red')
                        continue

                break
            except ValueError:
                click.secho('Wrong enter data!', fg='red')
                continue
        else:
            break

    return date


@click.command()
@click.option('--path', help='Path to file.')
@click.option('--name', help='Employee name to search or `-`')
@click.option('--start', help='Date start search or `-`')
@click.option('--stop', help='Date stop search or `-`')
@click.option('--summ', help='Sum work time [y/n]')
def run(path, name, start, stop, summ) -> None:
    if not path:
        path_to_file = _get_list_file_selection()
    else:
        path_to_file = path

    select_file = "You file selected: {}".format(click.style(path_to_file,
                                                             fg='green'))

    click.clear()
    click.echo(select_file)

    if not name:
        employee_name = _get_selection_employee(path_to_file)
    elif name == "''":
        employee_name = '-'
    else:
        employee_name = name

    select_name = "You employee selected: {}".format(click.style(employee_name,
                                                                 fg='green'))

    click.clear()
    click.echo(select_file)
    click.echo(select_name)

    click.clear()

    if not start:
        from_ = _get_from_date()
    elif start == "''":
        from_ = ''
    else:
        from_ = start

    select_from = "From: {}".format(click.style(from_ or '-', fg='green'))

    click.clear()
    click.echo(select_from)

    if not stop and stop != '-':
        to_ = _get_to_date(from_)
    elif stop == "''":
        to_ = ''
    else:
        to_ = stop

    select_to = "To: {}".format(click.style(to_ or '-', fg='green'))

    click.clear()
    click.echo(select_file)
    click.echo(select_name)
    click.echo(select_from)
    click.echo(select_to)

    if summ == "''" or not summ:
        sum_ = click.confirm("Sum work time ?", default=False)
    elif summ == 'y':
        sum_ = True
    else:
        sum_ = False

    click.echo(f"Sum work time: {click.style(str(sum_), fg='green')}")

    begin_time = datetime.datetime.now()

    work_time = get_total_work_time(path_to_file=path_to_file,
                                    employee_name=employee_name,
                                    from_=from_, to_=to_, sum_=sum_)

    endtime = datetime.datetime.now() - begin_time

    click.clear()
    click.echo(select_file)
    click.echo(select_name)
    click.echo(select_from)
    click.echo(select_to)
    click.echo(f"Sum work time: {click.style(str(sum_), fg='green')}")

    click.secho('=' * 55, fg='green')

    if work_time:
        click.echo(
            f'{click.style("Name".ljust(16), fg="yellow", bold=True)}'
            f'| {click.style("Work time", fg="yellow", bold=True)}'
        )

        for name, time in work_time.items():
            if type(time) == list:
                click.secho(name, fg='green', bold=True)
                click.echo(time)
                click.secho('=' * 100, fg='yellow')
            else:
                click.echo(f'{name.ljust(15)} | {time}')
    else:
        click.echo("Data not found !")

    click.echo('\n')

    if endtime:
        click.secho(str(f"Time execution: {endtime}"), fg='yellow', bold=True)

    return None


if __name__ == '__main__':
    run()
