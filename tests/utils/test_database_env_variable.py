"""
Test that I can switch between test and prod database via an env file
"""
import os


def test_read_db_env_variable():
    db_file = os.environ["KNOWLEDGE_DB_FILE"]
    assert db_file == "test.db"
