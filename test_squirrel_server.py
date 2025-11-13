import http.client
import json
import os
import pytest
import shutil
import subprocess
import sys
import time
import urllib

from squirrel_db import SquirrelDB

todo = pytest.mark.skip(reason='todo: pending spec')

def describe_squirrel_server():

    @pytest.fixture(autouse=True)
    def setup_and_cleanup_database():
        # setup the database
        shutil.copyfile('squirrel_db.db.template', 'squirrel_db.db')
        yield
        # clean up the database
        os.remove('squirrel_db.db')

    @pytest.fixture(autouse=True, scope='session')
    def start_and_stop_server():
        # run the server
        proc = subprocess.Popen([sys.executable, 'squirrel_server.py'])
        time.sleep(0.1)
        yield
        # stop the server process
        proc.kill()

    @pytest.fixture
    def http_client():
        conn = http.client.HTTPConnection('localhost:8080')
        return conn

    @pytest.fixture
    def request_body():
        return urllib.parse.urlencode({ 'name': 'Sam', 'size': 'large' })

    @pytest.fixture
    def request_headers():
        return { 'Content-Type': 'application/x-www-form-urlencoded' }

    @pytest.fixture
    def db():
        return SquirrelDB()

    # @pytest.fixture
    # def db():
    #     conn = sqlite3.connect('squirrel_db.db')
    #     return conn.cursor()

    @pytest.fixture
    def make_a_squirrel(db):
        db.createSquirrel("Fred", "small")

    def describe_get_squirrels():

        def it_returns_200_status_code(http_client):
            http_client.request("GET", "/squirrels")
            response = http_client.getresponse()
            http_client.close()

            assert response.status == 200

        def it_returns_json_content_type_header(http_client):
            http_client.request("GET", "/squirrels")
            response = http_client.getresponse()
            http_client.close()

            assert response.getheader('Content-Type') == "application/json"

        def it_returns_empty_json_array(http_client):
            http_client.request("GET", "/squirrels")
            response = http_client.getresponse()
            response_body = response.read()
            http_client.close()

            # assert response_body == b'[]'
            assert json.loads(response_body) == []

        def it_returns_json_array_with_one_squirrel(http_client, make_a_squirrel):
            http_client.request("GET", "/squirrels")
            response = http_client.getresponse()
            response_body = response.read()
            http_client.close()

            assert json.loads(response_body) == [{ 'id': 1, 'name': 'Fred', 'size': 'small' }]

    def describe_create_squirrel():

        def it_returns_201_status_code(http_client, request_body, request_headers):
            http_client.request("POST", "/squirrels", request_body, request_headers)
            response = http_client.getresponse()
            http_client.close()

            assert response.status == 201

        def it_creates_the_squirrel_in_the_database(http_client, request_body, request_headers, db):
            http_client.request("POST", "/squirrels", request_body, request_headers)
            response = http_client.getresponse()
            http_client.close()

            assert db.getSquirrels() == [{ 'id': 1, 'name': 'Sam', 'size': 'large' }]

