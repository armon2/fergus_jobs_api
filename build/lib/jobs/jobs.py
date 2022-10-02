import json

from flask import abort, Blueprint, request, Response

from jobs.jobs_service import create_new_job_and_get_id, query_jobs, query_job_by_id, update_job_status

bp = Blueprint('job', __name__, url_prefix='')

"""
API:
GET /tradie/{tradie_id}?status=completed&start_date=...&end_date=...&sort=...&order=...
POST /tradie/{tradie_id}
GET /tradie/{tradie_id}/job/{job_id}
PATCH /tradie/{tradie_id}/job/{job_id}
GET /tradie/{tradie_id}/job/{job_id}/notes
POST /tradie/{tradie_id}/job/{job_id}/notes
"""


# TODO: Authentication and authorization required before going to production!
@bp.route('/tradie/<int:tradie_id>/jobs', methods=('GET', 'POST'))
def tradie_jobs(tradie_id: int):
    if request.method == 'POST':
        post_data = request.get_json()
        new_job_id = create_new_job_and_get_id(tradie_id, post_data)
        return_json = json.dumps({'job_id': new_job_id})
        return Response(return_json, status=201, mimetype='application/json')

    elif request.method == 'GET':
        request_params = request.args.to_dict()
        job_records = query_jobs(tradie_id, request_params=request_params)
        return_json = json.dumps(job_records)
        return Response(return_json, status=200, mimetype='application/json')

    abort(404)


@bp.route('/tradie/<int:tradie_id>/job/<int:job_id>', methods=('GET', 'PATCH'))
def tradie_job(tradie_id: int, job_id: int):
    if request.method == 'GET':
        job_record = query_job_by_id(tradie_id, job_id)
        return_json = json.dumps(job_record)
        return Response(return_json, status=200, mimetype='application/json')

    elif request.method == 'PATCH':
        post_data = request.get_json()
        if 'status' not in post_data:
            abort(422, 'status value is required')
        try:
            job_record = update_job_status(tradie_id, job_id, post_data['status'])
        except Exception as e:
            abort(422, e)
        return_json = json.dumps(job_record)
        return Response(return_json, status=200, mimetype='application/json')

    abort(404)


@bp.route('/tradie/<int:tradie_id>/job/<int:job_id>/notes', methods=('GET', 'POST'))
def tradie_job_notes(tradie_id: int, job_id: int):
    # TODO: implement! out of time!
    abort(404, 'Not implemented')
