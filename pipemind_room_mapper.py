import os
import json
from datetime import datetime


class PipemindRoomNode:
    def __init__(self):
        self.room_name = ""
        self.description = ""
        self.north_connection = None
        self.east_connection = None
        self.south_connection = None
        self.west_connection = None
        self.id = str(id(self))
        self.connections = {}

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "room_name": ("STRING", {"default": "", "multiline": False}),
                "description": ("STRING", {"default": "", "multiline": True}),
                "export_map": ("BOOLEAN", {"default": False}),
                "map_name": ("STRING", {"default": "room_map", "multiline": False}),
            },
            "optional": {
                "north_input": ("ROOM",),
                "east_input": ("ROOM",),
                "south_input": ("ROOM",),
                "west_input": ("ROOM",),
            }
        }

    RETURN_TYPES = ("ROOM", "ROOM", "ROOM", "ROOM", "STRING")
    RETURN_NAMES = ("NORTH", "EAST", "SOUTH", "WEST", "room_info")
    FUNCTION = "process_room"
    CATEGORY = "pipemind/mapping"

    def connect_rooms(self, direction, other_room):
        if other_room:
            # Update connections dictionary and instance variables for this room
            self.connections[direction] = other_room
            if direction == "north":
                self.north_connection = other_room
                other_room.south_connection = self
                other_room.connections["south"] = self
            elif direction == "south":
                self.south_connection = other_room
                other_room.north_connection = self
                other_room.connections["north"] = self
            elif direction == "east":
                self.east_connection = other_room
                other_room.west_connection = self
                other_room.connections["west"] = self
            elif direction == "west":
                self.west_connection = other_room
                other_room.east_connection = self
                other_room.connections["east"] = self

    def get_all_rooms(self, visited=None):
        if visited is None:
            visited = {}

        if self.id in visited:
            return visited

        visited[self.id] = self

        connections = [
            self.north_connection,
            self.east_connection,
            self.south_connection,
            self.west_connection
        ]

        for connection in connections:
            if connection and connection.id not in visited:
                connection.get_all_rooms(visited)

        return visited

    def serialize_room(self):
        return {
            "id": self.id,
            "name": self.room_name,
            "description": self.description,
            "connections": {
                "north": self.north_connection.id if self.north_connection else None,
                "east": self.east_connection.id if self.east_connection else None,
                "south": self.south_connection.id if self.south_connection else None,
                "west": self.west_connection.id if self.west_connection else None
            }
        }

    def serialize_room_network(self):
        # First, get all rooms in the network
        all_rooms = self.get_all_rooms()

        # Create a list of all serialized rooms
        rooms_data = []
        for room in all_rooms.values():
            rooms_data.append(room.serialize_room())

        return {
            "rooms": rooms_data,
            "start_room": self.id
        }

    def export_to_json(self, map_name):
        output_dir = os.path.join(os.path.dirname(__file__), "room_maps")
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{map_name}_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)

        room_network = self.serialize_room_network()

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(room_network, f, indent=2)

        return filepath

    def process_room(self, room_name, description, export_map=False, map_name="room_map",
                     north_input=None, east_input=None, south_input=None, west_input=None):
        self.room_name = room_name
        self.description = description

        # Set up connections
        self.connect_rooms("north", north_input)
        self.connect_rooms("east", east_input)
        self.connect_rooms("south", south_input)
        self.connect_rooms("west", west_input)

        # Create room info string
        exits = []
        if self.north_connection: exits.append("North")
        if self.east_connection: exits.append("East")
        if self.south_connection: exits.append("South")
        if self.west_connection: exits.append("West")

        room_info = f"Room: {room_name}\nDescription: {description}\nExits: {', '.join(exits) if exits else 'None'}"

        # Export to JSON if requested
        if export_map:
            filepath = self.export_to_json(map_name)
            room_info += f"\nMap exported to: {filepath}"

        # Return connections and info
        return (
            self.north_connection,
            self.east_connection,
            self.south_connection,
            self.west_connection,
            room_info
        )