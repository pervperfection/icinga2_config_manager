import re
import argparse
from typing import Dict, List, Union
import logging

class ConfigItem:
    def __init__(self, item_type: str, name: str, attributes: Dict[str, Union[str, int, bool, List[str]]], raw_content: str = ""):
        self.item_type = item_type
        self.name = name
        self.attributes = attributes
        self.raw_content = raw_content  # Store the original content to preserve formatting
        self.imports = []  # To store special "import" attributes

    def update_attribute(self, key: str, value: Union[str, int, bool, List[str]]):
        """Update or add an attribute to the configuration item."""
        if key == "import":
            self.add_import(value)
        else:
            self.attributes[key] = value

    def add_import(self, import_value: str):
        """Handles the import attribute with a whitespace-delimited value."""
        if import_value not in self.imports:
            self.imports.append(import_value)

    def remove_attribute(self, key: str):
        """Remove an attribute from the configuration item."""
        if key in self.attributes:
            del self.attributes[key]
        elif key == "import":
            self.imports = []

    def serialize(self) -> str:
        """Serialize the object back into the original format, with updated attributes."""
        lines = [f'object {self.item_type} "{self.name}" {{']
        
        # Add import statements
        for imp in self.imports:
            lines.append(f'    import "{imp}"')
        
        # Add other attributes
        for key, value in self.attributes.items():
            if isinstance(value, list):
                value_str = f'[{", ".join(value)}]'
            elif isinstance(value, bool):
                value_str = 'true' if value else 'false'
            elif value.isdigit():
                value_str = value
            else:
                value_str = f'"{value}"' if isinstance(value, str) else str(value)
            lines.append(f'    {key} = {value_str}')
        
        lines.append('}')
        return "\n".join(lines)


class IcingaConfigParser:
    def __init__(self, config_text: str):
        self.config_text = config_text
        self.items: List[ConfigItem] = []

    def parse(self):
        """Parse the configuration file into ConfigItem objects."""
        # Regex to match the object blocks, preserving the original syntax
        object_re = re.compile(r'(object\s+(\w+)\s+"([^"]+)"\s*{([^}]*)})', re.MULTILINE | re.DOTALL)
        attr_re = re.compile(r'(\S+)\s*=\s*(.+)')
        import_re = re.compile(r'import\s+"([^"]+)"')

        for match in object_re.finditer(self.config_text):
            raw_content, item_type, item_name, body = match.groups()
            attributes = {}

            # Extract the attributes
            for attr_match in attr_re.finditer(body):
                key, value = attr_match.groups()
                value = value.strip()

                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value == "true":
                    value = True
                elif value == "false":
                    value = False
                elif value.startswith('[') and value.endswith(']'):
                    value = [v.strip() for v in value[1:-1].split(',')]
                attributes[key] = value

            # Extract the import attribute separately
            imports = []
            for imp_match in import_re.finditer(body):
                imports.append(imp_match.group(1))

            # Create a ConfigItem with the parsed data and raw content
            config_item = ConfigItem(item_type, item_name, attributes, raw_content)
            config_item.imports = imports  # Add imports to the item
            self.items.append(config_item)

    def get_items_by_type(self, item_type: str) -> List[ConfigItem]:
        """Retrieve all objects by their type."""
        return [item for item in self.items if item.item_type == item_type]

    def remove_items_by_type(self, item_type: str):
        """Remove all objects of a specific type."""
        self.items = [item for item in self.items if item.item_type != item_type]

    def add_item(self, item: ConfigItem):
        """Add a new configuration item to the list."""
        self.items.append(item)

    def serialize_config(self) -> str:
        """Serialize all items back to the original format."""
        return "\n\n".join(item.serialize() for item in self.items)

    def save_to_file(self, filepath: str):
        """Save the serialized configuration back to a file."""
        with open(filepath, 'w') as file:
            file.write(self.serialize_config())


# CLI-like interface functions
def read_config_file(filepath: str) -> str:
    """Read the configuration file content."""
    with open(filepath, 'r') as file:
        return file.read()

def edit_config_items(filepath: str, item_type: str, updates: Dict[str, Union[str, int, bool, List[str]]], remove_keys: List[str] = None):
    """Edit all configuration items of a specific type and save the updated config back to the file."""
    config_text = read_config_file(filepath)

    # Parse the config
    parser = IcingaConfigParser(config_text)
    parser.parse()

    # Find all items of the specified type
    items = parser.get_items_by_type(item_type)
    if items:
        for item in items:
            # Apply updates to each item of the specified type
            for key, value in updates.items():
                item.update_attribute(key, value)
            # Remove specified keys from each item
            if remove_keys:
                for key in remove_keys:
                    item.remove_attribute(key)
        
        # Save the updated config
        parser.save_to_file(filepath)
        logging.warning(f"\tUpdated all {item_type} objects in the configuration.")
    else:
        logging.warning(f"\tNo items of type {item_type} found in the configuration.")

def remove_type_from_config(filepath: str, item_type: str):
    """Remove all objects of a specific type from the configuration."""
    config_text = read_config_file(filepath)

    # Parse the config
    parser = IcingaConfigParser(config_text)
    parser.parse()

    # Remove the items of the specified type
    parser.remove_items_by_type(item_type)

    # Save the updated config
    parser.save_to_file(filepath)
    logging.warning(f"\tRemoved all {item_type} objects from the configuration.")

def write_new_object(filepath: str, item_type: str, name: str, attributes: Dict[str, Union[str, int, bool, List[str]]]):
    """Create and add a new configuration item to the file."""
    config_text = read_config_file(filepath)

    # Parse the config
    parser = IcingaConfigParser(config_text)
    parser.parse()

    # Create a new ConfigItem
    new_item = ConfigItem(item_type=item_type, name=name, attributes=attributes)

    # Add the new item
    parser.add_item(new_item)

    # Save the updated config
    parser.save_to_file(filepath)
    logging.warning(f"\tCreated new {item_type} object named '{name}' and saved to the configuration.")


# Function to parse CLI arguments
def parse_cli_args():
    parser = argparse.ArgumentParser(description="Edit Icinga configuration files.")
    
    # Arguments for file path and object type
    parser.add_argument('--file', '-f', required=True, help="Path to the Icinga configuration file")
    parser.add_argument('--type', '-t', required=True, help="Type of the configuration item (e.g., Host, Service, Endpoint)")
    
    # Add dynamic attribute changes
    parser.add_argument('--set', '-w', nargs=2, action='append', metavar=('key', 'value'), help="Set or update an attribute")
    
    # Remove attributes from object
    parser.add_argument('--remove', '-r', nargs='*', help="Remove specific attributes from objects of the specified type")
    
    # Remove entire object type
    parser.add_argument('--remove-type', '-rt', action='store_true', help="Remove all objects of a specific type from the configuration")
    
    # Create a new object
    parser.add_argument('--write-object', '-wo', action='store_true', help="Create a new object in the configuration")
    parser.add_argument('--name', '-n', help="Specify the name of the new object to create (used with --write-object)")

    parser.add_argument('--imports', '-i', help="Add an import to the object (e.g., --import generic-host)")

    return parser.parse_args()

def main():
    args = parse_cli_args()

    # Convert the --set key-value pairs into a dictionary
    updates = {}
    if args.set:
        for key, value in args.set:
            # Convert certain values like booleans and lists to proper types
            if value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            elif value.startswith('[') and value.endswith(']'):
                # Handle list format [item1, item2]
                value = [v.strip() for v in value[1:-1].split(',')]
            updates[key] = value

    # Handle import attribute if provided
    if args.imports:
        updates["import"] = args.imports

    # If --remove-type is specified, remove all objects of that type
    if args.remove_type:
        remove_type_from_config(args.file, args.type)
    # If --write-object is specified, create a new object
    elif args.write_object:
        if not args.name:
            logging.warning("\tError: --name is required when using --write-object")
        else:
            write_new_object(args.file, args.type, args.name, updates)
    else:
        # Call the edit function if not creating a new object
        edit_config_items(args.file, args.type, updates, remove_keys=args.remove)


if __name__ == "__main__":
    main()
