import os
from flask import Flask, render_template

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY= os.environ.get('SECRET_KEY') or 'dev_key',
        DATABASE_URL=os.environ['DATABASE_URL'],
        SSLMODE = "allow"
    )

    if test_config is not None:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    @app.route('/')
    def start():
        return render_template('main_page.html')


    from . import db, auth, tasting
    db.init_app(app)
    app.register_blueprint(tasting.bp)
    app.register_blueprint(auth.bp)
    app.add_url_rule('/', 'start')

    return app