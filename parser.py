from typing import Any
import sys


class Parser:
    """Parsing class. Contain only static methods"""

    @staticmethod
    def parse_config(filename: str) -> list[tuple[int, str, str]]:
        """Take config doc and stores it in a list of tuples"""
        config = []
        expected_keys = [
            "nb_drones",
            "start_hub",
            "end_hub",
            "hub",
            "connection"
        ]
        try:
            with open(filename) as f:
                i = 1
                for x in f:
                    line = x.strip()
                    if not line or line[0] == "#":
                        continue
                    if ":" not in line:
                        raise ValueError(f"Line {i}, invalid line: '{line}'")
                    name, value = line.split(":", 1)
                    name = name.strip()
                    value = value.strip()
                    if name not in expected_keys:
                        raise ValueError(f"Line {i}, invalid key: {name}")
                    config.append((i, name, value))
                    i += 1
        except FileNotFoundError:
            raise FileNotFoundError(f"File {filename} not found")
        except PermissionError:
            raise PermissionError(f"No permission for file {filename}")
        return config

    @staticmethod
    def check_no_dup(config: list[tuple[int, str, str]]) -> None:
        """Check if parameters are present once in config doc"""
        no_dup_keys = [
            "nb_drones",
            "start_hub",
            "end_hub"
        ]
        for key in no_dup_keys:
            count = 0
            for line, name, _ in config:
                if name == key:
                    count += 1
                    if count > 1:
                        raise ValueError(
                            f"line {line}, duplicate in config: {key}"
                        )
            if count == 0:
                raise ValueError(f"Missing parameter in config doc: {key}")

    @staticmethod
    def store_config_as_dict(
        config: list[tuple[int, str, str]]
    ) -> dict[str, Any]:
        """Store config in 3-entry dict: nb_drones, hubs and connections"""
        hubs: list[tuple[int, str, str]] = []
        connections: list[tuple[int, str]] = []
        config_dict: dict[str, Any] = {}
        try:
            Parser.check_no_dup(config)
        except ValueError as e:
            raise ValueError(e)
        for i, name, value in config:
            if name == "nb_drones":
                if i != 1:
                    raise ValueError(
                        "First line must define ther number of drones"
                    )
                try:
                    nb = int(value)
                    if nb <= 0:
                        raise ValueError(
                            f"Line {i}, {name} must be a positive integer"
                        )
                    config_dict["nb_drones"] = nb
                except ValueError as e:
                    raise ValueError(e)
            elif name == "connection":
                connections.append((i, value))
            else:
                hubs.append((i, name, value))
        if not connections:
            raise ValueError("No connection defined in config doc")
        config_dict["hubs"] = hubs
        config_dict["connections"] = connections
        return config_dict

    @staticmethod
    def parse_hub_metadata(data: str) -> dict[str, str]:
        """Store hub metadata in a dict"""
        parsed_data = {}
        metadata_keys = [
            "zone",
            "color",
            "max_drones"
        ]
        zone_types = [
            "normal",
            "blocked",
            "restricted",
            "priority"
        ]
        if not data or data[0] != "[" or data[-1] != "]":
            raise ValueError("hub metadata must be inside brackets")
        if "[" in data[1:-1] or "]" in data[1:-1]:
            raise ValueError("invalid hub metadata format")
        metadata = data[1:-1]
        for d in metadata.split():
            if d.count("=") != 1:
                raise ValueError("invalid hub metadata format")
            key, value = d.strip().split("=")
            if key not in metadata_keys:
                raise ValueError("Invalid hub metadata")
            elif key in parsed_data:
                raise ValueError("Duplicate in metadata")
            elif key == "max_drones":
                try:
                    nb = int(value)
                except ValueError:
                    raise ValueError("max_drones must be an int")
                if nb < 1:
                    raise ValueError("max_drones must be positive")
            elif key == "zone":
                if value not in zone_types:
                    raise ValueError(
                        "zone should be 'normal', 'blocked',"
                        " 'restricted' or 'priority'"
                    )
            elif key == "color":
                if not value.isalpha():
                    raise ValueError("invalid hub color")
            parsed_data[key] = value
        return parsed_data

    @staticmethod
    def parse_hubs(config: dict[str, Any], hub_names: set[str]) -> None:
        """Store parameters of each hub in a dict"""
        hubs: list[dict[str, Any]] = []
        hub_coord: set[tuple[int, int]] = set()
        for i, status, content in config["hubs"]:
            zone: dict[str, Any] = {}
            if status == "end_hub":
                zone["status"] = "end"
            elif status == "start_hub":
                zone["status"] = "start"
            parts = content.split()
            if len(parts) < 3 or any(p.startswith("[") for p in parts[:3]):
                raise ValueError(f"Line {i}, incomplete hub data")
            name, x, y = parts[:3]
            if "-" in name:
                raise ValueError(
                    f"Line {i}, zone name cannot contain dashes or spaces"
                )
            if name in hub_names:
                raise ValueError(f"Line {i}, duplicate in hub name")
            hub_names.add(name)
            zone["name"] = name
            try:
                zone["x"] = int(x)
                zone["y"] = int(y)
            except ValueError:
                raise ValueError(f"Line {i}, invalid hub data")
            if (zone["x"], zone["y"]) in hub_coord:
                raise ValueError(f"Line {i}, duplicate in hub coordinates")
            hub_coord.add((zone["x"], zone["y"]))
            try:
                raw_metadata = " ".join(content.split()[3:])
                if raw_metadata != "":
                    metadata = Parser.parse_hub_metadata(raw_metadata)
                    zone.update(metadata)
            except ValueError as e:
                raise ValueError(f"Line {i}, {e}")
            hubs.append(zone)
        config["hubs"] = hubs

    @staticmethod
    def parse_connections(
        config: dict[str, Any], hub_names: set[str]
    ) -> None:
        """Store each connection in a tuple"""
        connections: list[dict[Any, Any]] = []
        for i, edge in config["connections"]:
            connection = {}
            if edge.count("-") != 1:
                raise ValueError(f"Line {i}, invalid connection syntax")
            parts = edge.split()
            if not parts or len(parts) > 2:
                raise ValueError(f"Line {i}, invalid connection syntax")
            edge = parts[0]
            if len(parts) == 2:
                metadata = parts[1]
                if not metadata.startswith("[") or not metadata.endswith("]"):
                    raise ValueError(f"Line {i}, invalid connection metadata")
                metadata = metadata[1:-1]
                if metadata.count("=") != 1:
                    raise ValueError(f"Line {i}, invalid connection metadata")
                key, value = metadata.split("=")
                if key != "max_link_capacity":
                    raise ValueError(f"Line {i}, invalid connection metadata")
                try:
                    capacity = int(value)
                except ValueError:
                    raise ValueError(f"Line {i}, invalid capacity value")
                if capacity < 1:
                    raise ValueError(
                        f"Line {i}, max capacity must be positive"
                    )
                connection[key] = capacity
            start, end = edge.split("-")
            if not start or not end:
                raise ValueError(f"Line {i}, hub missing in connection")
            if start not in hub_names:
                raise ValueError(f"Line {i}, {start} is not a valid hub")
            if end not in hub_names:
                raise ValueError(f"Line {i}, {end} is not a valid hub")
            if start == end:
                raise ValueError(
                    f"Line {i}, {start}-{end} is not a valid connection"
                )
            connection["node_1"] = start
            connection["node_2"] = end
            connections.append(connection)
        roads = []
        for c in connections:
            a = c["node_1"]
            b = c["node_2"]
            road = set([a, b])
            if road in roads:
                raise ValueError(f"Connection {a}-{b} is duplicate")
            else:
                roads.append(road)
        config["connections"] = connections

    @staticmethod
    def parser(filename: str) -> dict[str, Any]:
        """Call all parsing methods, catch errors and return program data"""
        try:
            config = Parser.parse_config(filename)
            data = Parser.store_config_as_dict(config)
            hub_names: set[str] = set()
            Parser.parse_hubs(data, hub_names)
            Parser.parse_connections(data, hub_names)
        except ValueError as e:
            print(f"Invalid config format: {e}")
            sys.exit(1)
        except FileNotFoundError as e:
            print(f"File not found: {e}")
            sys.exit(1)
        except UnicodeDecodeError as e:
            print(f"Encoding error (file is not UTF-8): {e}")
            sys.exit(1)
        return data
