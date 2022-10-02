import datetime
import enum
import sqlite3
from dataclasses import dataclass
from time import strptime
from typing import List, Dict, Optional, Tuple, Union

from flask import abort

from jobs.db import get_db

PAGINATION_SIZE = 10

# Allowed keys to sort on
ALLOWED_SORT_KEYS = {
    'status': 'status',
    'date': 'created_at',
    'client': 'client_id',
}

# Used as keys in the json output
OUTPUT_FIELD_KEYS = ['Job ID', 'Client ID', 'Status', 'Title', 'Description', 'Created Time']


class JobStatus(enum.Enum):
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    INVOICING = "invoicing"
    TO_PRICED = "to priced"
    COMPLETED = "completed"


@dataclass
class Job:
    tradie_id: int
    client_id: int
    status: JobStatus
    title: str
    description: Optional[str]

    def __post_init__(self):
        errors = []
        for field_name in self.__annotations__.keys():
            # Crude validation here!
            # TODO: meaningfully validate input such as phone and address
            if field_name != 'job_description' and not getattr(self, field_name):
                human_readable_name = field_name.replace('_', ' ').capitalize()
                errors.append(f'{human_readable_name} is required')
        if errors:
            raise ValueError('. '.join(errors))


def create_new_job_and_get_id(tradie_id: int, post_data: Dict[str, str]) -> int:
    """
    Creates a new job in the database and returns its ID
    :param tradie_id:
    :param post_data: dictionary of keyed properties
    :return: ID of new job
    :exception: Exception is thrown if operation fails
    """
    try:
        job = Job(
            int(tradie_id),
            int(post_data['client_id']),
            JobStatus(post_data['status']),
            post_data['title'],
            post_data.get('description'),
        )
    except ValueError as e:
        abort(422, e)

    job_id = insert_job_row(job)
    return job_id


def insert_job_row(job: Job) -> int:
    db_cursor = get_db().cursor()
    try:
        db_cursor.execute(
            """
            INSERT INTO jobs (tradie_id, client_id, status, title, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            (job.tradie_id, job.client_id, job.status.value, job.title, job.description),
        )
        get_db().commit()
        return db_cursor.lastrowid
    except Exception as e:
        breakpoint()
        # todo: Granular & custom exception handling
        abort(500)


def query_job_by_id(tradie_id: int, job_id: int) -> Union[List[Dict[str, any]], Dict[str, any]]:
    db = get_db()
    # TODO use an ORM such as SQLAlchemy instead of constructing the query piecemeal
    db_cursor = db.execute(
        """
        SELECT id, client_id, status, title, description, created_at
        FROM jobs
        WHERE id = ? AND tradie_id = ?
        """,
        (job_id, tradie_id)
    )
    try:
        db_row = db_cursor.fetchone()
    except Exception:
        abort(500)

    if db_row is None:
        abort(404, 'Job not found')

    try:
        return get_formatted_output_job_data([db_row], multiple_items=False)
    except Exception:
        # todo: Granular & custom exception handling
        abort(500)


def update_job_status(tradie_id: int, job_id: int, new_status: str) -> Union[List[Dict[str, any]], Dict[str, any]]:
    try:
        # validate status value
        JobStatus(new_status)
    except ValueError:
        # todo: make the error more helpful
        abort(422, 'invalid status value')
    db = get_db()
    job_record = query_job_by_id(tradie_id, job_id)
    if job_record['Status'] == new_status:
        # status is the same, return the job unchanged
        return job_record
    try:
        db.execute(
            """
            UPDATE jobs
            SET status = ?
            WHERE id = ? AND tradie_id = ?
            """,
            (new_status, job_id, tradie_id)
        )
        db.commit()
        job_record['Status'] = new_status
        return job_record
    except Exception:
        abort(500)


def query_jobs(tradie_id: int, page_size: int = PAGINATION_SIZE, **request_params):
    db = get_db()
    # TODO use an ORM such as SQLAlchemy instead of constructing the query piecemeal
    sql_stmt = """
        SELECT id, client_id, status, title, description, created_at
        FROM jobs
        WHERE tradie_id = ?
    """
    page = 0
    sort_key, sort_order = None, None
    sql_params = [tradie_id]
    try:
        for key, val in request_params.items():
            if key == 'status':
                sql_stmt += ' AND status = ?'
                sql_params.append(val)
            elif key == 'client':
                sql_stmt += ' AND client_id = ?'
                sql_params.append(val)
            elif key == 'start_date':
                validate_input_date(val)
                sql_stmt += ' AND julianday(created_at) >= julianday(?)'
                sql_params.append(val)
            elif key == 'end_date':
                validate_input_date(val)
                sql_stmt += ' AND julianday(created_at) <= julianday(?)'
                sql_params.append(val)
            elif key == 'page':
                page = int(val)
            elif key == 'sort':
                sort_key = val
            elif key == 'order':
                sort_order = val
    except Exception as e:
        abort(422, e)

    # sorting
    sort_param_tuple = get_sql_sorting(sort_key, sort_order)
    sql_stmt += ' ORDER BY ?'
    sql_params.append(' '.join(sort_param_tuple))

    # pagination
    limit = page_size
    offset = page * page_size
    sql_stmt += ' LIMIT ? OFFSET ?'
    sql_params.extend([limit, offset])

    try:
        db_cursor = db.execute(sql_stmt, tuple(sql_params))
        db_rows = db_cursor.fetchall()
        result = get_formatted_output_job_data(db_rows)
        return result
    except Exception:
        # todo: Granular & custom exception handling
        abort(500)


def get_formatted_output_job_data(
    db_rows: List[sqlite3.Row], multiple_items: bool = True
) -> Union[List[Dict[str, any]], Dict[str, any]]:
    rows = list()
    for db_row in db_rows:
        row_dict = dict()
        for field_key, field_val in zip(OUTPUT_FIELD_KEYS, db_row):
            if isinstance(field_val, datetime.datetime):
                row_dict[field_key] = field_val.isoformat()
            else:
                row_dict[field_key] = field_val
        rows.append(row_dict)
    return rows if multiple_items else rows[0]


def get_sql_sorting(input_sort: Optional[str], input_order: Optional[str]) -> Tuple[str, str]:
    if input_sort:
        if input_sort in ALLOWED_SORT_KEYS:
            sort_key = ALLOWED_SORT_KEYS[input_sort]
        else:
            allowed = ', '.join(ALLOWED_SORT_KEYS.keys())
            raise Exception(f'sort should be one of {allowed}')
    else:
        sort_key = ALLOWED_SORT_KEYS['date']

    if input_order:
        if input_order not in {'asc', 'desc'}:
            raise Exception(f'order should be asc or desc')

    sort_order = input_order or 'desc'

    return sort_key, sort_order


def validate_input_date(date_str: str):
    try:
        strptime(date_str, '%Y-%m-%d')
    except ValueError:
        raise Exception('Date must be in YYYY-MM-DD format')
