from lxml.etree import Element, SubElement, tostring
from datetime import datetime
from random import randint, choice
from names import get_first_name, get_last_name

_DATE_TIME_FORMAT = '%d-%m-%Y %H:%M:%S'


def _generate_employees() -> list:
    gfn, gln = get_first_name, get_last_name
    return list([f"{gfn()[0].lower()}.{gln().lower()}" for _ in range(1, 115)])


def _normalize_datetime(start_time: dict) -> bytes:
    str_time_compile = "{d}-{m}-{y} {H}:{M}:{S}".format(**start_time)
    return str(datetime.strptime(str_time_compile, _DATE_TIME_FORMAT)).encode(
        encoding="utf=8")


def _generate_work_time() -> list:
    year = randint(2015, 2020)
    day = randint(1, 28)
    month = randint(1, 12)
    hour = randint(8, 17)

    start_time = dict(d=day, m=month, y=year, H=hour,
                      M=randint(0, 59), S=randint(0, 59))

    end_time = dict(d=day, m=month, y=year, H=hour + randint(1, 5),
                    M=randint(0, 59), S=randint(0, 59))

    start_time = _normalize_datetime(start_time)
    end_time = _normalize_datetime(end_time)

    return [start_time, end_time]


def generate(records: int = 100, file_name="work_time_employees"):
    with open(f'xml/{file_name}.xml', 'wb') as fp:
        people = Element('people')
        employees = _generate_employees()

        for i in range(records):
            person = SubElement(people, "person")
            start = SubElement(person, "start")
            end = SubElement(person, "end")

            person.set("full_name", choice(employees))

            start.text, end.text = _generate_work_time()

        xml_ = tostring(
            people,
            pretty_print=True,
            xml_declaration=True,
            encoding='UTF-8',
        )

        fp.write(xml_)


if __name__ == '__main__':
    generate(records=1000, file_name="work_time_employees")
    generate(records=100000, file_name="big_work_time_employees")
    generate(records=1000000, file_name="very_big_work_time_employees")
    pass
