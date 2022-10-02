import os

from flask import Flask


# Mostly boilerplate code here
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',  # TODO: use a secret manager
        DATABASE=os.path.join(app.instance_path, 'jobs.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.errorhandler(404)
    def not_found(e):
        return 'Resource Not Found', 404

    @app.errorhandler(422)
    def invalid_input(e):
        return f'Error: {str(e)}', 422

    from . import db
    db.init_app(app)

    from jobs import jobs
    app.register_blueprint(jobs.bp)

    return app
