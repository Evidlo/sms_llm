#!/usr/bin/env python3

import os
import json


class JSONDatabase:
    """
    A simple database backed by JSON files.

    This class allows you to store and retrieve data using JSON files as the backend storage.
    It supports caching of accessed entries and writing them back to the files either immediately
    or during a sync or close operation.

    Attributes:
        directory (str): The directory where the JSON files are stored.
    """

    def __init__(self, directory):
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)
        self.cache = {}

    def __getitem__(self, key):
        if key not in self.cache:
            file_path = os.path.join(self.directory, f"{key}.json")
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    self.cache[key] = json.load(f)
            else:
                self.cache[key] = []
        return self.cache[key]

    def __setitem__(self, key, value):
        self.cache[key] = value
        self._save_to_file(key)

    def _save_to_file(self, key):
        file_path = os.path.join(self.directory, f"{key}.json")
        with open(file_path, 'w') as f:
            json.dump(self.cache[key], f, indent=4)

    def __contains__(self, key):
        """Checks if a JSON file for the key exists in the directory."""
        file_path = os.path.join(self.directory, f"{key}.json")
        return os.path.exists(file_path)

    def sync(self, key=None):
        """
        Writes the cached data back to their respective JSON files.
        If a key is provided, only that key is synced. Otherwise, all keys are synced.
        """
        if key:
            self._save_to_file(key)
        else:
            for key in self.cache:
                self._save_to_file(key)

    def close(self):
        """Writes back all changes and clears the cache."""
        self.sync()  # Ensure all changes are written back
        self.cache.clear()