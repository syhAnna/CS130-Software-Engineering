import pytest
from flaskr import create_app

headers = {'Content-Type': 'application/json'}
app = create_app()

def test_login():
    with app.test_client() as c:
        response = c.get("/auth/register")
        status_code = response.status_code
        assert status_code == 200

        with c.session_transaction() as sess:
            sess['imagecode'] = '11'
        input_data = {"username": "test3", "password": "test33", "repassword": "test33", "email": "test3@test3", "imagecode": "11"}
        response = c.post("/auth/register", data=input_data, follow_redirects=True)
        # this will create a user name test3!   

