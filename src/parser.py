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
    except ValueError as v:
        raise ParseException("wrong db_drones format: invalid value")
    return value
# unknown option prefix. Valid options: color=, max_drones=

def parse_options(opts: str, normal_hub: bool):
    result = {}
    valid_prefixes = ("max_drones=", "color=", "zone=")

    if not opts.startswith('[') or not opts.endswith(']'):
        raise ParseException("wrong [options] format: should be [] included")
    opts = opts.lstrip('[').rstrip(']').split() # handling any [] sucession weird behavior
    if not normal_hub and any(arg.startswith("zone=") for arg in opts):
        raise ParseException("start/end_hub won't need the zone option")
    if not opts:
        raise ParseException("empty options space :(") 
    if any(not arg.startswith(valid_prefixes) for arg in opts):
        raise ParseException("wrong [options] format: choose from color=, zone=, or max_drones=")

    for arg in opts:
        if "max_drones" in arg:
            if "max_drones" in result:
                raise ParseException("wrong [options] format: use only unique args")
            try:
                max_drones = int(arg[len("max_drones="):]) 
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
    return(result)


def parse_hub(line: str, normal_hub: bool) -> tuple[str, int, int, str | None]:
    hub = {}
    values = line.strip().split(None, 4) # default consecutive spaces handeled 
    hub["type"] = values.pop(0)[:-1] # removing the :
    if len(values) >= 3:
        hub["name"] = values[0]
        if " " in hub["name"] or "-" in hub["name"]:
            raise ParseException("spaces and - are forbidden in names")
        try:
            hub["x"], hub["y"] = int(values[1]), int(values[2])
        except ValueError as v:
            raise ParseException("invalid coordinates values")
    if len (values) == 4:
        hub["options"] = parse_options(values[3], normal_hub)
    return(hub)

def parser(file_name: str) -> None:
    """Parse the input file and build the graph."""
    hubs: dict[str, Hub] = {}
    connections: list[Connection] = []
    nb_drones: int | None = None
    start_hub: Hub | None = None
    end_hub: Hub | None = None

    with open(file_name, 'r') as f:
        for line_num, raw_line in enumerate(f, start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            if line.startswith("nb_drones:"):
                if nb_drones is not None:
                    raise ParseException(f"line {line_num}: duplicate nb_drones")
                nb_drones = parse_nb_drones(line, line_num)

            elif line.startswith("start_hub:"):
                if nb_drones is None:
                    raise ParseException(f"line {line_num}: nb_drones must come first")
                if start_hub is not None:
                    raise ParseException(f"line {line_num}: duplicate start_hub")
                start_hub = parse_hub(line, line_num)
                check_duplicate_name(start_hub.name, hubs, line_num)
                hubs[start_hub.name] = start_hub

            elif line.startswith("end_hub:"):
                if nb_drones is None:
                    raise ParseException(f"line {line_num}: nb_drones must come first")
                if end_hub is not None:
                    raise ParseException(f"line {line_num}: duplicate end_hub")
                end_hub = parse_hub(line, line_num)
                check_duplicate_name(end_hub.name, hubs, line_num)
                hubs[end_hub.name] = end_hub

            elif line.startswith("hub:"):
                if nb_drones is None:
                    raise ParseException(f"line {line_num}: nb_drones must come first")
                hub = parse_hub(line, line_num)
                check_duplicate_name(hub.name, hubs, line_num)
                hubs[hub.name] = hub

            # elif line.startswith("connection:"):
            #     conn = parse_connection(line, hubs, line_num)
            #     connections.append(conn)

            else:
                raise ParseException(f"line {line_num}: unrecognized line format")

    if nb_drones is None:
        raise ParseException("missing nb_drones")
    if start_hub is None:
        raise ParseException("missing start_hub")
    if end_hub is None:
        raise ParseException("missing end_hub")


def check_duplicate_name(name: str, hubs: dict[str, "Hub"], line_num: int) -> None:
    """Raise if hub name already exists."""
    if name in hubs:
        raise ParseException(f"line {line_num}: duplicate hub name '{name}'")
                
            #     hub = 
                    
            # elif line.startswith("hub"):
            #     parse_hub(line, True)
            # parse_hub(line, False)


parser("./../maps/medium/01_dead_end_trap.txt")