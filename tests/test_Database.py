'''
Created on Feb 12, 2017
Updated on Jun 17, 2018
@author: matt.hess@lookoutmountainresearch.com
'''
import sys, os.path
import pytest
app_dir = (os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) + '\\app\\')
sys.path.append(app_dir)
import lmr_secrets
import Database

@pytest.fixture()
def resource():
    print("Setup Database Tests...")
    # Insert code to test database functions.
    db_secrets = lmr_secrets.load_db_secrets()
    yield "Testing database functions..."
    # Insert code to undo the database tests.
    print("Teardown Database Tests Complete.")

def test_db_create_table():
    #
    pass

def test_db_insert():
    pass

def test_db_query():
    pass

def test_db_update():
    pass
