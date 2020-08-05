from flask import (
    Blueprint, request, redirect, url_for, render_template, flash
)
import sys

from grogg_app.auth import login_required

bp = Blueprint('tasting', __name__, url_prefix='/tasting')

@bp.route('/participate', methods=('GET', 'POST'))
def participate():
    pass


@bp.route('/manage', methods=('GET', 'POST'))
@login_required
def manage():
    pass


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        # Information needed:
        # nickname
        # List of groggs: name, spirit, soft drink
        nickname = request.form['nickname']
        grogg_list = []
        grogg_list.append(request.form['grogg_1'])
        grogg_list.append(request.form['grogg_2'])
        grogg_list.append(request.form['grogg_3'])

        error = None

        if nickname is None:
            error = "Smeknamn krävs!"
        elif len(grogg_list) == 0 or None in grogg_list:
            error = "Groggar krävs!"

        if error is not None:
            flash(error)

        print("Nickname: {}".format(nickname), file=sys.stdout)
        print("Groggar: {}".format(grogg_list), file=sys.stdout)
        # Supposed to generated tasting code here

        # Add new tasting to db

        # Redirect it to the manage view
        # return redirect(url_for('tasting.manage'))

    else:
        return render_template('tasting/create.html')


@bp.route('/join', methods=('GET', 'POST'))
def join():
    pass