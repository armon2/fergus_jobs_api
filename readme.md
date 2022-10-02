# RESTful Jobs API for Fergus

## Installing and running the app

```bash
# create a python virtual
# Install the project and dependencies first
python setup.py install
# initialize the database next
flask --app jobs init-db
# Finally start the server
flask --app jobs run
```

Now you can use tools such as HTTP Client, Postman or cURL to make HTTP calls. Here are some examples:

```
### Create a new job
POST http://localhost:5000/tradie/1/jobs
Content-Type: application/json

{
  "client_id": 10,
  "status": "invoicing",
  "title": "Wiring job",
  "description": "Need tons of wires!"
}

### get a list of jobs, Ex 1
GET http://localhost:5000/tradie/1/jobs?sort=date&order=asc&status=active
Content-Type: application/json

### get a list of jobs, Ex 2
GET http://localhost:5000/tradie/1/jobs?sort=date&order=asc&client=123&status=scheduled
Content-Type: application/json

### get a list of jobs, Ex 3
GET http://localhost:5000/tradie/1/jobs?sort=date&order=desc&start_date=22-10-01
Content-Type: application/json

### get job with ID of 1
GET http://localhost:5000/tradie/1/job/1
Content-Type: application/json

### update the status of a job
PATCH http://localhost:5000/tradie/1/job/1
Content-Type: application/json

{
  "status": "invoicing"
}
```

## About the API

This API is backed by a sqlite database with two tables `jobs` and `job_notes`.
It is currently only implementing the Jobs API without Notes; job notes will be in the next release!
Current capabilities are as follows:

- POST: create a job:
    - `POST /tradie/<tradie_id>/jobs`
    - required input value fields are `client_id`, `status`, `title`, and `description` is optional; all str
    ```js
    {
      "client_id": 10,
      "status": "invoicing",
      "title": "the job title",
      "description": "optional job description"
    }
    ```
    - Output: Json in the form of `{"job_id": 123}`
- GET a list of jobs (paginated):
    - `GET /tradie/<tradie_id>/jobs`
    - input query parameters allowed (all optional):
        - `page`: int - default: 0; page size is hardcoded to 10.
        - `sort`: One of `status`, `date` (default), `client`
        - `order`: `asc` or `desc` (default)
        - `status` [Filter] One of `scheduled`, `active`, `invoicing`, `to priced`, or `completed`
        - `start_date` [Filter]: `YYYY-MM-DD` format
        - `end_date` [Filter]: `YYYY-MM-DD` format
    - Output: Json list of objects:
    - ```js
    [
      {
        "Job ID": 25,
        "Client ID": 123,
        "Status": "invoicing",
        "Title": "Broken pipe",
        "Description": "This is a quick task.",
        "Created Time": "2022-09-30T23:52:54"
      },
      { ... },
    ]
    ```
- GET a job by its ID:
    - GET `/tradie/<tradie_id>/job/<job_id>`
    - Output: Json object:
  - ```js
    {
      "Job ID": 25,
      "Client ID": 123,
      "Status": "invoicing",
      "Title": "Broken pipe",
      "Description": "This is a quick task.",
      "Created Time": "2022-09-30T23:52:54"
    }
    ```
- PATCH update the status of a job:
    - PATCH `/tradie/<tradie_id>/job/<job_id>`
    - Input: Requires json with `status` key
    - Output: Json object
    - ```js
    {
      "Job ID": 25,
      "Client ID": 123,
      "Status": "invoicing",
      "Title": "Broken pipe",
      "Description": "This is a quick task.",
      "Created Time": "2022-09-30T23:52:54"
    }
    ```


## Helpful commands

All commands are run from the application root

### Run tests using pytest

```bash
pytest
```

### To initialize or reset the database:

```bash
flask --app jobs init-db
```

### Running the application in debug mode:

```bash
flask --app jobs --debug run
```

### What's next?

- Improving the database model
- Increasing test coverage and adding unit tests
- Adding Logging
- Use OpenAPI/Swagger for API documentation
- Better documentation in the code
- Implementing job notes
- Implementing an aggregator service to return client contact info
- Improving configuration and using secret management
- Containerizing the app
- Adding authn/z
- and much more...