#!/usr/bin/env python3

import pytest
from database import JSONDatabase

def test_database(tmp_path):

    directory = tmp_path

    db = JSONDatabase(directory)

    assert 'foo' not in db

    db['foo'] = []

    assert 'foo' in db

    db['foo'].append(1)

    assert len(db['foo']) > 0