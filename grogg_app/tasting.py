from flask import (
    Blueprint, request, redirect, url_for, render_template, flash, g
)
from datetime import datetime
import random

from grogg_app.auth import login_required
from grogg_app.db import get_db

bp = Blueprint('tasting', __name__, url_prefix='/tasting')

@bp.route('/participate', methods=('GET', 'POST'))
def participate():
    pass


@bp.route('/manage', methods=('GET', 'POST'))
#TODO: This one next
@login_required
def manage():
    pass


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':

        tasting_name = request.form['tasting_name']
        grogg_string = request.form['grogg_list']

        # TODO - remove these lines
        print("tasting_name: {}".format(tasting_name), flush=True)
        print("Groggar: {}".format(grogg_string), flush=True)
        print(str(tasting_name is None))

        error = None

        if len(tasting_name) == 0:
            error = "Namn på provningen krävs!"
        elif len(grogg_string) == 0:
            print("Huston", flush=True)
            error = "Groggar krävs!"

        print(error)
        if error is not None:
            print("error is not none", flush=True)
            flash(error)

        # Split the string with groggs into substring and put in list
        grogg_list = grogg_string.split(';')
        grogg_list = [grogg.rstrip() for grogg in grogg_list]
        grogg_list = [grogg.lstrip() for grogg in grogg_list]
        print("Grogg list: {}".format(grogg_list), flush=True)


        # Created by
        user_id = g.user['id']
        print(user_id, flush=True)
        # Created time
        created = datetime.today().isoformat()
        # Join code
        code = str(random.randint(1, 9999))
        while len(code) < 4: code = '0' + code

        # Establish connection to db
        conn = get_db()
        cur = conn.cursor()
        # Add new tasting to db
        cur.execute("INSERT INTO tastings (tasting_name, created_by, created_time, join_code, grogg_list) \
                    VALUES (%s, %s, %s, %s, %s);", (tasting_name, user_id, created, code, grogg_list))

        conn.commit()

        cur.close()
        # Redirect it to the manage view
        return redirect(url_for('tasting.manage'))


    return render_template('tasting/create.html')


@bp.route('/join', methods=('GET', 'POST'))
def join():
    pass