import datetime

from memory_profiler import profile
from lxml import etree

_DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
_DATE_FORMAT = '%Y-%m-%d'


def _normalize_datetime(start_time: str) -> "datetime.datetime.strptime":
    try:
        return datetime.datetime.strptime(str(start_time), _DATE_TIME_FORMAT)
    except ValueError:
        try:
            return datetime.datetime.strptime(str(start_time), _DATE_FORMAT)
        except ValueError:
            raise


def get_total_work_time(path_to_file: str,
                        employee_name: str = '',
                        from_: str = '',
                        to_: str = '',
                        summ: bool = True) -> dict:
    context = _get_context(path_to_file)

    work_list = {}

    for event, elem in context:
        full_name = elem.attrib.get('full_name')
        start = elem.find('start')
        end = elem.find('end')

        _clear_context(elem)

        if from_:
            if from_ := _normalize_datetime(from_):
                _start = _normalize_datetime(start.text)

                if not _start >= from_:
                    continue

        if to_:
            if to_ := _normalize_datetime(to_):
                _end = _normalize_datetime(end.text)

                if not _end <= to_:
                    continue

        if employee_name != '-' and full_name != employee_name:
            continue

        if full_name not in work_list:
            work_list[full_name] = []

        work_list[full_name].append({
            'start': start.text,
            'end': end.text,
        })

    if summ:
        total_work_times = {}

        for full_name, times in work_list.items():
            common_times = datetime.timedelta(0)

            for time in times:
                end = _normalize_datetime(time['end'])
                start = _normalize_datetime(time['start'])
                delta = end - start

                common_times += delta

            total_work_times.update({
                full_name: str(common_times)
            })

        return total_work_times if total_work_times else None

    return work_list if work_list else None


@profile
def filtering_by_name(file_name: str, employee_name: str = '') -> None:
    context = _get_context(file_name)

    for event, elem in context:
        full_name = elem.attrib.get('full_name')

        start = elem.find('start')
        end = elem.find('end')

        if full_name == employee_name:
            print({'full_name': full_name, 'start': start.text, 'end': end.text,})
        else:
            print({'full_name': full_name, 'start': start.text, 'end': end.text,})

        _clear_context(elem)

    return None


def get_all_employees(file_name: str) -> list:
    context = _get_context(file_name)

    list_full_name = []

    for event, elem in context:
        full_name = elem.attrib.get('full_name')

        if full_name not in list_full_name:
            list_full_name.append(full_name)

        _clear_context(elem)

    return sorted(list_full_name)


def _clear_context(elem: etree._Element) -> None:
    elem.clear()

    while elem.getprevious() is not None:
        del elem.getparent()[0]

    return None


def _get_context(file_name: str) -> "etree.iterparse":
    context = etree.iterparse(file_name, tag='person')
    return context


if __name__ == '__main__':
    # print(get_all_employees('xml/work_time_employees.xml'))
    # filtering_by_name('xml/work_time_employees.xml')
    # filtering_by_name('xml/middle_work_time_employees.xml')
    filtering_by_name('xml/big_work_time_employees.xml')
    # filtering_by_name('xml/very_big_work_time_employees.xml')

    # get_total_work_time('xml/work_time_employees.xml', employee_name='-')
    # get_total_work_time('xml/middle_work_time_employees.xml', employee_name='-')
    # get_total_work_time('xml/big_work_time_employees.xml', employee_name='-', summ=False)
    # get_total_work_time('xml/very_big_work_time_employees.xml', employee_name='-', summ=False)
    pass
