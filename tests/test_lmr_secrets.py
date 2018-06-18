'''
Created: 6/17/18
Author: matt.hess@LookoutMountainResearch.com
'''
import sys, os.path
app_dir = (os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) + '\\app\\')
sys.path.append(app_dir)

def is_not_empty(var):
    if var is None:
        return False
    else:
        return True

def test_lmr_secrets():
    try:
        import lmr_secrets
    except ModuleNotFoundError as e:
        print(e)
    db_secrets = lmr_secrets.load_db_secrets()

    assert is_not_empty(db_secrets['db_hostname']) == True
    assert is_not_empty(db_secrets['db_user']) == True
    assert is_not_empty(db_secrets['db_instance']) == True
    assert is_not_empty(db_secrets['db_password']) == True
