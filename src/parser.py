import sys
# from models import ZoneType
from exceptions import *
from models import *

hubs = []

def parse_nb_drones(line: str) -> int:
    if not line.startswith("nb_drones:"):
        raise ParseException("wrong nb_drones format: missing 'nb_drones:' prefix")
    remaining = line[len("nb_drones:"):].strip()
    if not remaining:
        raise ParseException("wrong db_drones format: missing '<number>' suffix")
    try:
        value = int(remaining)
        if value <= 0:
            raise ParseException("wrong db_drones format: negative or null value")
    except ValueError as v:
        raise ParseException("wrong db_drones format: invalid value")
    return value

def parse_hub(line: str) -> tuple[str, int, int, str | None]:
    values = line[len("start_hub:"):].strip().split(' ')
    # try:
    [name, x, y] = values[:3]
    print(name)
    print(x)
    print(y)
    #     if ' ' in name or '-' in name:
    #         raise ParseException("Zone names can use any valid characters but dashes and spaces.")
    #     [x, y] = int(x) , int(y)
    #     if x < 0 or y < 0:
    #         raise ParseException("coordinates can't be negative")
    # except ValueError as v:
    #     raise ParseException(v.message)
    # color = color.strip('[]')[len("color="):]
    # return None


def parser(file_name: str):
    with open(file_name, 'r') as f:
        count = 0
        start_hub = None
        end_hub = None
        for line in f:
            line = line.strip(' ')
            if line.startswith(("#", "\n")):
                continue
            if count == 0:
                nb_drone = parse_nb_drones(line)
                count +=1
            elif line.startswith("start_hub:") and count == 1:
                if start_hub is not None:
                    raise ParseException("only one start_hub is required")
                else:
                    start_hub_data = parse_hub(line)
                    count +=1
            elif line.startswith("hub:") and count == 2:
                hub1 = parse_hub(line)

parser("./../medium/01_dead_end_trap.txt")
