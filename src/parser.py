"""Parser module for the Fly-in drone routing system."""

from typing import Any

from exceptions import ParseException
from models import Hub, Connection, Graph, HubType, ZoneType


class Parser:
    """Parses a Fly-in map file into a Graph object."""

    def __init__(self, file_name: str) -> None:
        """Initialize the parser with a file path."""
        self.file_name = file_name
        self.hubs: list[Hub] = []
        self.connections: list[Connection] = []
        self.nb_drones: int | None = None
        self.start_hub: Hub | None = None
        self.end_hub: Hub | None = None

    def parse(self) -> Graph:
        """Read the file, validate it, and return a Graph."""
        with open(self.file_name, 'r') as f:
            for line_num, raw_line in enumerate(f, start=1):
                line = raw_line.split("#", 1)[0].strip()
                if not line:
                    continue
                self._dispatch_line(line, line_num)

        if self.nb_drones is None:
            raise ParseException(
                "missing nb_drones declaration"
            )
        if self.start_hub is None:
            raise ParseException(
                "missing start_hub declaration"
            )
        if self.end_hub is None:
            raise ParseException(
                "missing end_hub declaration"
            )

        return Graph(
            self.nb_drones,
            self.hubs,
            self.connections,
            self.start_hub,
            self.end_hub
        )

    def _dispatch_line(
        self, line: str, line_num: int
    ) -> None:
        """Route a line to the appropriate handler."""
        if line.startswith("nb_drones:"):
            self._handle_nb_drones(line, line_num)
        elif line.startswith("start_hub:"):
            self._handle_start_hub(line, line_num)
        elif line.startswith("end_hub:"):
            self._handle_end_hub(line, line_num)
        elif line.startswith("hub:"):
            self._handle_hub(line, line_num)
        elif line.startswith("connection:"):
            self._handle_connection(line, line_num)
        else:
            raise ParseException(
                f"line {line_num}: unrecognized line format"
            )

    def _handle_nb_drones(
        self, line: str, line_num: int
    ) -> None:
        """Handle an nb_drones line."""
        if self.nb_drones is not None:
            raise ParseException(
                f"line {line_num}: "
                "duplicate nb_drones declaration"
            )
        self.nb_drones = self._parse_nb_drones(
            line, line_num
        )

    def _handle_start_hub(
        self, line: str, line_num: int
    ) -> None:
        """Handle a start_hub line."""
        if self.nb_drones is None:
            raise ParseException(
                f"line {line_num}: "
                "nb_drones must be declared first"
            )
        if self.start_hub is not None:
            raise ParseException(
                f"line {line_num}: "
                "duplicate start_hub declaration"
            )
        self.start_hub = self._parse_hub(line, line_num)
        self._check_duplicates(self.start_hub, line_num)
        self.hubs.append(self.start_hub)

    def _handle_end_hub(
        self, line: str, line_num: int
    ) -> None:
        """Handle an end_hub line."""
        if self.nb_drones is None:
            raise ParseException(
                f"line {line_num}: "
                "nb_drones must be declared first"
            )
        if self.end_hub is not None:
            raise ParseException(
                f"line {line_num}: "
                "duplicate end_hub declaration"
            )
        self.end_hub = self._parse_hub(line, line_num)
        self._check_duplicates(self.end_hub, line_num)
        self.hubs.append(self.end_hub)

    def _handle_hub(
        self, line: str, line_num: int
    ) -> None:
        """Handle a hub line."""
        if self.nb_drones is None:
            raise ParseException(
                f"line {line_num}: "
                "nb_drones must be declared first"
            )
        hub = self._parse_hub(line, line_num)
        self._check_duplicates(hub, line_num)
        self.hubs.append(hub)

    def _handle_connection(
        self, line: str, line_num: int
    ) -> None:
        """Handle a connection line."""
        if self.nb_drones is None:
            raise ParseException(
                f"line {line_num}: "
                "nb_drones must be declared first"
            )
        if self.start_hub is None:
            raise ParseException(
                f"line {line_num}: "
                "start_hub must be declared before connections"
            )
        if self.end_hub is None:
            raise ParseException(
                f"line {line_num}: "
                "end_hub must be declared before connections"
            )
        connection = self._parse_connection(line, line_num)
        self._check_dup_connections(connection, line_num)
        self.connections.append(connection)

    def _parse_nb_drones(
        self, line: str, line_num: int
    ) -> int:
        """Extract and validate the nb_drones value."""
        remaining = line[len("nb_drones:"):].strip()
        if not remaining:
            raise ParseException(
                f"line {line_num}: "
                "missing value after nb_drones:"
            )
        try:
            nb_drones = int(remaining)
            if nb_drones <= 0:
                raise ParseException(
                    f"line {line_num}: "
                    "nb_drones must be a positive integer"
                )
        except ValueError:
            raise ParseException(
                f"line {line_num}: "
                "nb_drones must be a positive integer"
            )
        return nb_drones

    def _parse_options(
        self, opts_str: str, line_num: int
    ) -> dict[str, Any]:
        """Parse a bracket-enclosed metadata block."""
        result: dict[str, Any] = {}
        defaults: dict[str, Any] = {
            'zone': 'normal',
            'color': None,
            'max_drones': 1,
        }
        valid_prefixes = (
            "max_drones=", "color=", "zone="
        )

        if (not opts_str.startswith('[')
                or not opts_str.endswith(']')):
            raise ParseException(
                f"line {line_num}: "
                "options must be enclosed in []"
            )
        tokens = opts_str[1:-1].split()
        if not tokens:
            raise ParseException(
                f"line {line_num}: empty options block"
            )
        if any(
            not arg.startswith(valid_prefixes)
            for arg in tokens
        ):
            raise ParseException(
                f"line {line_num}: invalid option key, "
                "expected zone=, color=, or max_drones="
            )

        for arg in tokens:
            if arg.startswith("max_drones="):
                if "max_drones" in result:
                    raise ParseException(
                        f"line {line_num}: "
                        "duplicate 'max_drones' option"
                    )
                try:
                    max_drones = int(
                        arg[len("max_drones="):]
                    )
                except ValueError:
                    raise ParseException(
                        f"line {line_num}: "
                        "max_drones must be a valid integer"
                    )
                if max_drones <= 0:
                    raise ParseException(
                        f"line {line_num}: max_drones "
                        "must be a positive integer"
                    )
                result["max_drones"] = max_drones

            elif arg.startswith("color="):
                if "color" in result:
                    raise ParseException(
                        f"line {line_num}: "
                        "duplicate 'color' option"
                    )
                color = arg[len("color="):]
                if not color:
                    raise ParseException(
                        f"line {line_num}: "
                        "color value cannot be empty"
                    )
                if "-" in color:
                    raise ParseException(
                        f"line {line_num}: "
                        "color name cannot contain '-'"
                    )
                result["color"] = color

            elif arg.startswith("zone="):
                if "zone" in result:
                    raise ParseException(
                        f"line {line_num}: "
                        "duplicate 'zone' option"
                    )
                zone = arg[len("zone="):]
                valid_zones = [
                    z.value for z in ZoneType
                ]
                if zone not in valid_zones:
                    raise ParseException(
                        f"line {line_num}: "
                        f'invalid zone type "{zone}"'
                    )
                result["zone"] = zone

        return {**defaults, **result}

    def _parse_hub(
        self, line: str, line_num: int
    ) -> Hub:
        """Parse a hub, start_hub, or end_hub line."""
        values = line.strip().split(None, 4)
        options: dict[str, Any] = {
            'zone': 'normal',
            'color': None,
            'max_drones': 1,
        }
        length = len(values)

        if length < 4 or length > 5:
            raise ParseException(
                f"line {line_num}: expected "
                "4 or 5 arguments for hub definition"
            )

        hub_type = values[0][:-1]
        valid_types = [t.value for t in HubType]
        if hub_type not in valid_types:
            raise ParseException(
                f"line {line_num}: "
                f"unknown hub type '{hub_type}'"
            )
        name = values[1]
        if "-" in name or " " in name:
            raise ParseException(
                f"line {line_num}: "
                "hub name cannot contain '-' or spaces"
            )
        try:
            x, y = int(values[2]), int(values[3])
            if x < 0 or y < 0:
                raise ParseException(
                    f"line {line_num}: "
                    "coordinates cannot be negative"
                )
        except ValueError:
            raise ParseException(
                f"line {line_num}: "
                "coordinates must be valid integers"
            )

        if length == 5:
            options = self._parse_options(
                values[4], line_num
            )

        return Hub(
            hub_type, name, x, y,
            options["zone"],
            options["color"],
            options["max_drones"],
        )

    def _parse_connection(
        self, line: str, line_num: int
    ) -> Connection:
        """Parse a connection line."""
        values = line.strip().split()
        max_link = 1
        length = len(values)

        if length < 2 or length > 3:
            raise ParseException(
                f"line {line_num}: expected "
                "2 or 3 arguments for connection"
            )

        link = values[1].split('-')
        if len(link) != 2 or not link[0] or not link[1]:
            raise ParseException(
                f"line {line_num}: invalid "
                f"connection format '{values[1]}'"
            )
        if link[0] == link[1]:
            raise ParseException(
                f"line {line_num}: "
                "self connection isn't accepted"
            )
        hub_names = {h.name for h in self.hubs}
        if any(
            zone not in hub_names for zone in link
        ):
            raise ParseException(
                f"line {line_num}: "
                "connection references undefined hub"
            )

        if length == 3:
            max_link = self._parse_connection_opts(
                values[2], line_num
            )

        return Connection(link[0], link[1], max_link)

    def _parse_connection_opts(
        self, raw: str, line_num: int
    ) -> int:
        """Parse the optional metadata of a connection."""
        if not raw.startswith('[') or not raw.endswith(']'):
            raise ParseException(
                f"line {line_num}: connection "
                "options must be enclosed in []"
            )
        tokens = raw[1:-1].split()
        if len(tokens) != 1:
            raise ParseException(
                f"line {line_num}: connection "
                "accepts only max_link_capacity="
            )
        if not tokens[0].startswith("max_link_capacity="):
            raise ParseException(
                f"line {line_num}: invalid option for "
                "connection, expected max_link_capacity="
            )
        try:
            max_link = int(
                tokens[0][len("max_link_capacity="):]
            )
        except ValueError:
            raise ParseException(
                f"line {line_num}: max_link_capacity "
                "must be a valid integer"
            )
        if max_link <= 0:
            raise ParseException(
                f"line {line_num}: max_link_capacity "
                "must be a positive integer"
            )
        return max_link

    def _check_duplicates(
        self, hub: Hub, line_num: int
    ) -> None:
        """Check for name or coordinate conflicts."""
        for h in self.hubs:
            if h.name == hub.name:
                raise ParseException(
                    f"line {line_num}: "
                    f"duplicate hub name '{hub.name}'"
                )
            if h.x == hub.x and h.y == hub.y:
                raise ParseException(
                    f"line {line_num}: duplicate "
                    f"coordinates ({hub.x}, {hub.y})"
                )

    def _check_dup_connections(
        self, con: Connection, line_num: int
    ) -> None:
        """Check for duplicate connections (a-b == b-a)."""
        for c in self.connections:
            if (
                (con.hub_a == c.hub_a
                 and con.hub_b == c.hub_b)
                or (con.hub_a == c.hub_b
                    and con.hub_b == c.hub_a)
            ):
                raise ParseException(
                    f"line {line_num}: duplicate "
                    f"connection '{con.hub_a}-{con.hub_b}'"
                )
