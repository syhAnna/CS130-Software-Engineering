import pytest
import string
import random
from flaskr import create_app

headers = {'Content-Type': 'application/json'}
app = create_app()
c = app.test_client()

def string_in_page(str_list, page):
    if isinstance(str_list, str):
        str_list = [str_list]
    for string in str_list:
        if string not in page:
            return False, string
    return True, ""

def check_get(url, expected_string):
    response = c.get(url)
    status_code, resp_data = response.status_code, str(response.data)
    assert status_code == 200, f"{url} GET Error: {status_code}"
    ok, err_string = string_in_page(expected_string, resp_data)
    assert ok, f"{url} GET Error: {err_string} not exists in return content"

def check_post(url, expected_string, request):
    response = c.post(url, data=request, follow_redirects=True)
    status_code, resp_data = response.status_code, str(response.data)
    assert status_code == 200, f"{url} Post Error: {status_code}"
    ok, err_string = string_in_page(expected_string, resp_data)
    assert ok, f"{url} POST Error: {err_string} not exists in return content"

def test_register():
    check_get(url="/auth/register", 
              expected_string=["Username", "Password", "Email", "Verification", "Register"])

    with c.session_transaction() as sess:
        sess['imagecode'] = '11'
    # a failing register
    register_request = {
        "username": "test3", 
        "password": "test33", 
        "repassword": "test33", 
        "email": "test3@gmail.com", 
        "imagecode": "11"
    }
    check_post(url="/auth/register", 
               request=register_request,
               expected_string="is already registered.")
    
    # a randomly generated username to make sure it's new
    username = str(random.randint(0, 9)).join(random.sample(string.ascii_letters, 6))
    register_request = {
        "username": username, 
        "password": "test33", 
        "repassword": "test33", 
        "email": "test3@gmail.com", 
        "imagecode": "11"
    }
    check_post(url="/auth/register", 
               request=register_request,
               expected_string="Login</button>")


def test_login():
    check_get(url="/auth/login",
              expected_string="Login</button>")

    with c.session_transaction() as sess:
        sess['imagecode'] = '11'
    login_request = {
        "username": "test3", 
        "password": "test333", 
        "imagecode": "11"
    }
    check_post(url="/auth/login", 
                request=login_request,
                expected_string=["Password Incorrect", "Login</button>"])

    login_request = {
        "username": "test3", 
        "password": "test33", 
        "imagecode": "11"
    }
    check_post(url="/auth/login", 
                request=login_request,
                expected_string=["Type", "City", "Start", "End", "Search"])


def test_user_profile():
    user_id = 11
    with c.session_transaction() as sess:
        sess['user_id'] = user_id
    check_get(url=f"/user/home/{user_id}",
              expected_string=["test3", "test3@gmail.com", "Recent Published"])
    
    # TODO[yikai]: write test for set functions
    
def test_main_page():
    check_get(url=f"/",
              expected_string=["Type: TODO", "City", "Start", "End", "Publish New Post"])
    
    check_get(url="/ViewPost/1",
              expected_string=["Type:", "TODO", "comment 1"])
    # TODO[yikai]: write test for search functions

def test_create_pet():
    user_id = 7
    with c.session_transaction() as sess:
        sess['user_id'] = user_id
    create_request = {"age": 1, "weight": 10, "type": "dog", "description": "cute dog", "city": "Los Angeles"}
    check_post(url="/create", request=create_request, expected_string="")

    



    
    

