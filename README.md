# Icinga Configuration Editor

**WIP**
script is not ideal but gets simple job done via cli.
Python script to manage icinga2 configuration

This Python script is designed to help you manage and manipulate Icinga configuration files.

# Features
Edit Configuration Items: Update or set specific attributes for objects of a given type in an Icinga configuration file.

Remove Attributes: Remove specified attributes from objects of a particular type.

Remove Entire Object Types: Recursively remove all objects of a specific type.

Create New Objects: Add new objects with specified attributes to the configuration file.

# Requirements
Python 3.x

# Command-Line Arguments
  --file or -f: Specify the path to the Icinga configuration file.

  --type or -t: Define the type of the configuration object (e.g., Host, Service, Endpoint).

  --set or -w: Set or update an attribute for objects of the specified type. Takes two arguments: the attribute key and the value.

  --remove or -r: Remove specific attributes from all objects of the specified type.

  --remove-type or -rt: Remove all objects of the specified type from the configuration.

  --write-object or -wo: Create a new object with the specified attributes.

  --name or -n: Specify the name for the new object (used with --write-object).

  --imports or -i: Add an import to an object.

# Examples
Edit an object: Update the check_interval attribute for all Host objects in the configuration:
```
  python /path/to/script/icinga_manager.py --file config.conf --type Host --set check_interval "90"
```
Remove an attribute: Remove the address attribute from all Host objects:
```
  python /path/to/script/icinga_manager.py --file config.conf --type Host --remove address
```
Remove an entire object type: Remove all Service objects from the configuration:
```
  python /path/to/script/icinga_manager.py --file config.conf --type Service --remove-type
```
Create a new object: Add a new Host object named new-host with specific attributes:
```
  python /path/to/script/icinga_manager.py --file config.conf --type Host --name new-host --write-object --set address "192.168.1.10"
```
