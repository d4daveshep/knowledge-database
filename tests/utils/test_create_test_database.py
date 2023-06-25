"""
Test the creation of a test database (using common fixtures)
"""
import os
from os import path


def create_test_database(temp_filename:str):
    with open(file=temp_filename,mode="x") as temp_file:
        temp_file.write('abc')


def test_create_test_database():
    
    
    temp_filename = "/tmp/test.db"
    if path.exists(temp_filename):
        os.remove(temp_filename)
    
    create_test_database(temp_filename)
    
    assert path.exists(temp_filename)
    assert path.getsize(temp_filename) > 0

    assert False, "TODO make this a database"

    