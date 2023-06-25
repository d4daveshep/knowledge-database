"""
Test that I can switch between test and prod database via an env file
"""
import os

from pydantic import BaseSettings, Field


def test_read_db_env_variable():
    db_file = os.environ["KNOWLEDGE_DB_FILE"]
    assert db_file == "test.db"
