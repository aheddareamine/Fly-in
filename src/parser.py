import sys
# from models import ZoneType
from exceptions import *
from models import *


def parse_nb_drones(line: str) -> int:
    if not line.startswith("nb_drones:"):
        raise ParseException("wrong nb_drones format: missing 'nb_drones:' prefix")
    remaining = line[len("nb_drones:"):].strip()
    if not remaining:
        raise ParseException("wrong db_drones format: missing '<number>' suffix")
    try:
        value = int(remaining)
    except ValueError as v:
        raise ParseException("wrong db_drones format: invalid value")
    return value

def parse_options(opts: str, normal_hub: bool):
    result = {}
    valid_prefixes = ("max_drones=", "color=", "zone=")

    if not opts.startswith('[') or not opts.endswith(']'):
        raise ParseException("wrong [options] format: should be [] included")
    opts = opts.lstrip('[').rstrip(']').split() # handling any [] sucession weird behavior
    print(opts)
    if any(not arg.startswith(valid_prefixes) for arg in opts):
        raise ParseException("wrong [options] format: unknown prefix")

    for arg in opts:
        if "max_drones" in arg:
            if "max_drones" in result:
                raise ParseException("wrong [options] format: use only unique args")
            try:
                max_drones = int(arg[len("max_drones="):])
                if max_drones <= 0:
                    raise ParseException("wrong options format: invalid max_drones value") 
                result["max_drones"] = max_drones
            except ValueError as v:
                raise ParseException("wrong [options] format: invalid max_drones value")

        if "color" in arg:
            if "color" in result:
                raise ParseException("wrong [options] format: use only unique args")
            if arg[len("color="):] == "":
                raise ParseException("wrong [options] format: no string color")
            result["color"] = arg[len("color="):] # color value won't be checked in parser

        if "zone" in arg:
            if "zone" in result:
                raise ParseException("wrong [options] format: use only unique args")
            if arg[len("zone="):] not in [z.value for z in ZoneType]:
                raise ParseException(f'wrong [options] format: "{arg[len("zone="):]}" not a zone type :)')
            result["zone"] = arg[len("zone="):]
    print(result)
    print(60*"=")

def parse_hub(line: str, normal_hub) -> tuple[str, int, int, str | None]:
    hub = {}
    values = line.strip().split(None, 4) # default consecutive spaces handeled 
    print(values)
    hub_type = values.pop(0)[:-1] # removing the :
    try:
        name, x, y, remaining = values[0], int(values[1]), int(values[2]), values[3]
        options = parse_options(remaining)
    except ValueError as v:
        raise ParseException("invalid coordinates values")
    # options = str(remaining).strip('[]').split(' ')
    # options = str(remaining).strip('[]').split(' ')
    # if len(remaining.split(' ')) >= 2:
    #     raise ParseException("wrong hub format: too many arguments")
    # print(options)
    # print(hub_type)
    # print(name)
    # print(x)
    # print(y)

    # for _ in options:
    #     print(_)
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
        phase = "drones"
        start_hub = None
        end_hub = None
        hubs = []
        for line in f:
            line = line.strip(' ')
            if line.startswith(("#", "\n")):
                continue
            if phase == "drones":
                nb_drone = parse_nb_drones(line)
                phase = "start_hub"
            elif phase == "start_hub":
                if start_hub != None:
                    raise ParseException("can't use more than 1 start_hub")
                start_hub = parse_hub(line, False)
                phase = "hubs"
            elif phase == "hubs":
                hub = parse_hub(line, True)
                if hub in hubs or hub.name == hub:
                    raise ParseException("")

                

            elif line.startswith("hub"):
                parse_hub(line, True)
            parse_hub(line, False)


parser("./../maps/medium/01_dead_end_trap.txt")
