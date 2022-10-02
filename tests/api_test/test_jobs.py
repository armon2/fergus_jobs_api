import json

from tests import *


def test_jobs_get_empty(client):
    response = client.get('/tradie/-1/jobs')
    assert response.json is None


def test_job_404(client):
    response = client.get('/tradie/5/job/-1')
    assert response.json is None
    assert response.status_code == 404


@pytest.fixture()
def jobs_list():
    return [
        {
            "Job ID": 20,
            "Client ID": 123,
            "Status": "active",
            "Title": "Install fans",
            "Description": "Needs to be done soon",
            "Created Time": "2022-09-30T23:52:54"
        },
        {
            "Job ID": 12,
            "Client ID": 20,
            "Status": "scheduled",
            "Title": "Repair pipe",
            "Description": "pipe leaks",
            "Created Time": "2022-10-01T17:04:53"
        },
        {
            "Job ID": 5,
            "Client ID": 10,
            "Status": "completed",
            "Title": "s21",
            "Description": "good desc",
            "Created Time": "2022-10-01T17:05:14"
        },
    ]


@pytest.fixture()
def jobs_input():
    return [
        {
            "client_id": 10,
            "status": "completed",
            "title": "s21",
            "description": "good desc"
        },
        {
            "client_id": 20,
            "status": "scheduled",
            "title": "Repair pipe",
            "description": "pipe leaks"
        },
        {
            "client_id": 123,
            "status": "active",
            "title": "Install fans",
            "description": "Needs to be done soon"
        },
    ]


def test_jobs(client, jobs_input, jobs_list):
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    post_res = client.post('/tradie/42/jobs', data=json.dumps(jobs_input[0]), headers=headers)
    assert post_res.status_code == 201
    assert post_res.json['job_id'] >= 1

    get_res = client.get('/tradie/42/jobs')
    assert get_res.status_code == 200
    get_json = get_res.json[0]
    for field_key in ['Client ID', 'Status', 'Title', 'Description']:
        # Verify the last item in job list equals the first created
        assert get_json[field_key] == jobs_list[-1][field_key]


def test_job(client, jobs_input, jobs_list):
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    post_res = client.post('/tradie/5/jobs', data=json.dumps(jobs_input[1]), headers=headers)
    assert post_res.status_code == 201
    job_id = post_res.json['job_id']
    assert job_id >= 1

    get_res = client.get(f'/tradie/5/job/{job_id}')
    assert get_res.status_code == 200
    for field_key in ['Client ID', 'Status', 'Title', 'Description']:
        # Verify the job equals the second created
        assert get_res.json[field_key] == jobs_list[1][field_key]

    # change the status
    assert get_res.json['Status'] == 'scheduled'
    patch_res = client.patch(f'/tradie/5/job/{job_id}', data=json.dumps({'status': 'invoicing'}), headers=headers)
    assert patch_res.status_code == 200
    assert patch_res.json['Status'] == 'invoicing'

    # make sure change persisted
    get_res_2 = client.get(f'/tradie/5/job/{job_id}')
    assert get_res_2.status_code == 200
    assert get_res_2.json['Status'] == 'invoicing'

