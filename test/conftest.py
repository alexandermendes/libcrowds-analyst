# -*- coding: utf8 -*-

import os
import json
import enki
import pytest
from pybossa_analyst.core import create_app

os.environ['PYBOSSA_ANALYST_SETTINGS'] = '../settings_test.py'
flask_app = create_app()


@pytest.fixture
def app(request):
    ctx = flask_app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return flask_app


@pytest.fixture
def test_client(app):
    return app.test_client()


@pytest.fixture
def login(test_client, app):
    data = {'api_key': app.config['API_KEY']}
    with test_client as c:
        c.post('/login', data=data)
        yield c


@pytest.fixture
def project():
    return enki.pbclient.DomainObject({
        "id": 1,
        "name": "Some Project",
        "short_name": "some_project",
        "webhook": "http://example.com",
    })


@pytest.fixture
def task(project):
    return enki.pbclient.DomainObject({
        "id": 42,
        "project_id": project.id,
        "info": {"url": "example.com", "title": "img.jpg"},
        "n_answers": 10,
        "quorum": 0,
        "calibration": 0,
        "state": "completed",
        "priority_0": 0.0
    })


@pytest.fixture
def result(project, task):
    return enki.pbclient.DomainObject({
        "id": 123,
        "project_id": project.id,
        "task_id": task.id,
        "info": None
    })


@pytest.fixture
def create_task_run(task, project):
    def create(id, info):
        return enki.pbclient.DomainObject({
            "id": id,
            "project_id": project.id,
            "info": info,
            "task_id": task.id,
        })
    return create


@pytest.fixture
def create_task_run_df(task, create_task_run):
    def create(task_run_info):
        tasks = [task]
        task_runs = []
        tr_data = {task.id: task_runs}

        # Create task runs using task run fixture as template
        for i in range(len(task_run_info)):
            tr = create_task_run(i, task_run_info[i])
            task_runs.append(tr)
        df = enki.dataframer.create_task_run_data_frames(tasks, tr_data)
        return df[task.id]
    return create


@pytest.fixture
def payload(project, task, result):
    load = dict(fired_at=u'2014-11-17 09:49:27',
                project_short_name=project.short_name,
                project_id=project.id,
                task_id=task.id,
                result_id=result.id,
                event=u'task_completed')
    return json.dumps(load)
