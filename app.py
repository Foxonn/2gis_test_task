import click
import os
import datetime
from memory_profiler import profile

from seeker import get_all_employees, _normalize_datetime, get_total_work_time


def _display_list_file_selection() -> list:
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

    select_file = f"You file selected:" \
                  f" {click.style(files[n].name, fg='green')}"

    return [os.path.abspath(files[n].path), select_file]


def _display_list_selection_employee(path_to_file: str) -> list:
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

    if name != '':
        select_name = f"You employee selected:" \
                      f" {click.style(name, fg='green')}"
    else:
        select_name = f"You employee selected:" \
                      f" {click.style('employee not specified', fg='green')}"

    return [name, select_name]


def _display_from_date() -> list:
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

    select_from = f"From: {click.style(date if date else '-', fg='green')}"

    return [date, select_from]


def _display_to_date(date_from) -> list:
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

    select_to = f"To: {click.style(date if date else '-', fg='green')}"

    return [date, select_to]


# @profile
def run() -> None:
    path_to_file, select_file = _display_list_file_selection()

    click.clear()
    click.echo(select_file)

    employee_name, select_name = _display_list_selection_employee(path_to_file)

    click.clear()
    click.echo(select_file)
    click.echo(select_name)

    click.clear()
    from_, select_from = _display_from_date()

    click.clear()
    click.echo(select_from)
    to_, select_to = _display_to_date(from_)

    click.clear()
    click.echo(select_file)
    click.echo(select_name)
    click.echo(select_from)
    click.echo(select_to)

    sum_ = click.confirm("Sum work time ?", default=False)

    click.secho("Please wait...", fg='green', bold=True)

    work_time = get_total_work_time(path_to_file=path_to_file,
                                    employee_name=employee_name, from_=from_,
                                    to_=to_, sum_=sum_)

    click.clear()
    click.echo(select_file)
    click.echo(select_name)
    click.echo(select_from)
    click.echo(select_to)
    click.echo(f"Sum work time: {click.style(str(sum_), fg='green')}")

    click.secho('=' * 55, fg='green')

    begin_time = datetime.datetime.now()

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

    if begin_time:
        click.secho(
            str(f"Time execution: {datetime.datetime.now() - begin_time}"),
            fg='yellow', bold=True
        )

    return None


if __name__ == '__main__':
    run()
