# pylint: disable=missing-module-docstring,missing-function-docstring
import os.path

from fastapi.testclient import TestClient
import sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from utils import utils



from tasklist.main import app

client = TestClient(app)

app.dependency_overrides[utils.get_config_filename] = \
    utils.get_config_test_filename


def setup_database():
    scripts_dir = os.path.join(
        os.path.dirname(__file__),
        '..',
        'database',
        'migrations',
    )
    config_file_name = utils.get_config_test_filename()
    secrets_file_name = utils.get_admin_secrets_filename()
    utils.run_all_scripts(scripts_dir, config_file_name, secrets_file_name)


def test_read_main_returns_not_found():
    setup_database()
    response = client.get('/')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}


def test_read_tasks_with_no_task():
    setup_database()
    response = client.get('/task')
    assert response.status_code == 200
    assert response.json() == {}


def test_create_and_read_some_tasks():
    setup_database()

    user = {"name":"zé"}
    response = client.post('/user', json=user)
    user_uuid =  response.json()

    tasks = [
        {
            "description": "foo",
            "completed": False,
            "userID": user_uuid
        },
        {
            "description": "bar",
            "completed": True,
            "userID": user_uuid
        },
        {
            "description": "baz",
            "userID": user_uuid
        },
        {
            "completed": True,
            "userID": user_uuid
        },
        {
            "userID": user_uuid
        },
    ]
    expected_responses = [
        {
            'description': 'foo',
            'completed': False,
            "userID": user_uuid
        },
        {
            'description': 'bar',
            'completed': True,
            "userID": user_uuid
        },
        {
            'description': 'baz',
            'completed': False,
            'userID': user_uuid
        },
        {
            'description': 'no description',
            'completed': True,
            'userID': user_uuid
        },
        {
            'description': 'no description',
            'completed': False,
            'userID': user_uuid
        },
    ]

    # Insert some tasks and check that all succeeded.
    uuids = []
    for task in tasks:
        response = client.post("/task", json=task)
        assert response.status_code == 200
        uuids.append(response.json())

    # Read the complete list of tasks.
    def get_expected_responses_with_uuid(completed=None):
        return {
            uuid_: response
            for uuid_, response in zip(uuids, expected_responses)
            if completed is None or response['completed'] == completed
        }

    response = client.get('/task')
    assert response.status_code == 200
    assert response.json() == get_expected_responses_with_uuid()

    # Read only completed tasks.
    for completed in [False, True]:
        response = client.get(f'/task?completed={str(completed)}')
        assert response.status_code == 200
        assert response.json() == get_expected_responses_with_uuid(completed)

    # Delete all tasks.
    for uuid_ in uuids:
        response = client.delete(f'/task/{uuid_}')
        assert response.status_code == 200

    # Check whether there are no more tasks.
    response = client.get('/task')
    assert response.status_code == 200
    assert response.json() == {}


def test_substitute_task():
    setup_database()

    user = {'name': 'zé'}
    response = client.post('/user', json=user)
    assert response.status_code == 200
    useruuid_ = response.json()
    # Create a task.
    task = {'description': 'foo', 'completed': False, 'userID': useruuid_}
    response = client.post('/task', json=task)
    assert response.status_code == 200
    uuid_ = response.json()

    # Replace the task.
    new_task = {'description': 'bar', 'completed': True, 'userID': useruuid_}
    response = client.put(f'/task/{uuid_}', json=new_task)
    assert response.status_code == 200

    # Check whether the task was replaced.
    response = client.get(f'/task/{uuid_}')
    assert response.status_code == 200
    assert response.json() == new_task

    # Delete the task.
    response = client.delete(f'/task/{uuid_}')
    assert response.status_code == 200


def test_alter_task():
    setup_database()

    user = {'name': 'zé'}
    response = client.post('/user', json=user)
    assert response.status_code == 200
    useruuid_ = response.json()

    # Create a task.
    task = {'description': 'foo', 'completed': False, 'userID': useruuid_}
    response = client.post('/task', json=task)
    assert response.status_code == 200
    uuid_ = response.json()

    # Replace the task.
    new_task_partial = {'completed': True, 'userID': useruuid_}
    response = client.patch(f'/task/{uuid_}', json=new_task_partial)
    assert response.status_code == 200

    # Check whether the task was altered.
    response = client.get(f'/task/{uuid_}')
    assert response.status_code == 200
    assert response.json() == {**task, **new_task_partial}

    # Delete the task.
    response = client.delete(f'/task/{uuid_}')
    assert response.status_code == 200


def test_read_invalid_task():
    setup_database()

    response = client.get('/task/invalid_uuid')
    assert response.status_code == 422


def test_read_nonexistant_task():
    setup_database()

    response = client.get('/task/3668e9c9-df18-4ce2-9bb2-82f907cf110c')
    assert response.status_code == 404


def test_delete_invalid_task():
    setup_database()

    response = client.delete('/task/invalid_uuid')
    assert response.status_code == 422


def test_delete_nonexistant_task():
    setup_database()

    response = client.delete('/task/3668e9c9-df18-4ce2-9bb2-82f907cf110c')
    assert response.status_code == 404


def test_delete_all_tasks():
    setup_database()

    user = {'name': 'zé'}
    response = client.post('/user', json=user)
    assert response.status_code == 200
    uuid_ = response.json()

    # Create a task.
    task = {'description': 'foo', 'completed': False, 'userID': uuid_}
    response = client.post('/task', json=task)
    assert response.status_code == 200
    uuid_ = response.json()

    # Check whether the task was inserted.
    response = client.get('/task')
    assert response.status_code == 200
    assert response.json() == {uuid_: task}

    # Delete all tasks.
    response = client.delete('/task')
    assert response.status_code == 200

    # Check whether all tasks have been removed.
    response = client.get('/task')
    assert response.status_code == 200
    assert response.json() == {}



def test_read_user_with_no_user():
    setup_database()
    response = client.get('/user')
    assert response.status_code == 200
    assert response.json() == {}

def update_user():
    setup_database()
    user = {"name":"zé"}
    response_get = client.get('/user', json=user)
    user_uuid =  response_get.json()

    new_user = {"name":"zinho"}

    response_put = client.patch(f'/user/{user_uuid}', json=new_user)

    response_delete = client.delete(f"/user/{user_uuid}")

    assert response_put.status_code == 200
    assert response_delete.status_code == 200

def test_create_and_delete_user():
    setup_database()

    user = {"name":"zé"}
    response = client.post('/user', json=user)
    user_uuid =  response.json()

    response2 = client.delete(f"/user/{user_uuid}")
    assert response.status_code == 200

def test_create_and_read_user():
    setup_database()

    user = {"name":"zé"}

    response1 = client.post('/user', json=user)

    user_uuid =  response1.json()

    response2 = client.get(f"/user/{user_uuid}")

    assert response1.status_code == 200
    assert response2.status_code == 200

def test_read_users_with_no_user():
    setup_database()
    response = client.get("/user")
    assert response.status_code == 200
    assert response.json() == {}


def test_read_nonexistant_user():
    setup_database()

    response = client.get('/user/3668e9c9-df18-4ce2-9bb2-82f907cf110c')
    assert response.status_code == 404

