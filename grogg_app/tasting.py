from flask import (
    Blueprint, request, redirect, url_for, render_template, flash, g, session
)
from datetime import datetime
import random

from grogg_app.auth import join_required, login_required
from grogg_app.db import get_db
from grogg_app.utils import tasting_entry_as_dict, update_ratings_list, update_rated_by_list

bp = Blueprint('tasting', __name__, url_prefix='/tasting')


@bp.route('/<int:id>/participate', methods=('GET', 'POST'))
@join_required
def participate(id):
    # Get tasting to manage
    #TODO: Duplicated code with manage
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tastings WHERE id=%s;", (id,))
    current_tasting = cur.fetchone()

    if current_tasting is None:
        flash("Invalid tasting.")
        redirect(url_for("start"))

    tasting_dict = tasting_entry_as_dict(current_tasting)
    tasting_name = tasting_dict['tasting_name']
    current_grogg = tasting_dict['grogg_list'][tasting_dict['current_grogg_idx']]
    join_code = tasting_dict['join_code']

    if request.method == 'POST':
        current_guest = session['nickname']
        grogg_idx = tasting_dict['current_grogg_idx']

        rated_by = tasting_dict['rated_by']
        try:
            rated_by[grogg_idx]
        except IndexError:
            rated_by.append([])

        # Check that guest has not already voted
        if current_guest in rated_by[grogg_idx]:
            flash("Du har redan röstat, ditt fule fan!")
            return render_template('tasting/participate.html', tasting_name=tasting_name,
                           current_grogg=current_grogg, join_code=join_code, tasting_id=id)

        update_rated_by_list(rated_by, grogg_idx, current_guest)

        ratings = tasting_dict['ratings']
        try:
            ratings[grogg_idx]
        except IndexError:
            ratings.append([])

        update_ratings_list(ratings, grogg_idx,
                            [int(request.form['taste']), int(request.form['smell']), int(request.form['feeling'])])

        conn = get_db()
        cur = conn.cursor()
        cur.execute("UPDATE tastings SET ratings = %s, rated_by = %s WHERE id = %s;",
                    (ratings, rated_by, id)
                    )
        conn.commit()
        cur.close()
        return render_template('tasting/participate.html', tasting_name=tasting_name,
                           current_grogg=current_grogg, join_code=join_code, tasting_id=id)


    return render_template('tasting/participate.html', tasting_name=tasting_name,
                           current_grogg=current_grogg, join_code=join_code, tasting_id=id)


@bp.route('/<int:id>/manage', methods=('GET', 'POST'))
#TODO: This one next
@login_required
def manage(id):
    # Get tasting to manage
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tastings WHERE id=%s;", (id,))
    current_tasting = cur.fetchone()

    if current_tasting is None:
        flash("Invalid tasting.")
        redirect(url_for("start"))

    tasting_dict = tasting_entry_as_dict(current_tasting)

    # Verify that correct user is logged in.
    if g.user['id'] != tasting_dict['created_by']:
        flash("Skaparen av provningen ej inloggad!")
        redirect(url_for("start"))

    if request.method == 'POST':
        # Increment grogg_idx by one if not completed
        tasting_dict['current_grogg_idx'] += 1
        sql = "UPDATE tastings SET current_grogg_idx = %s WHERE id = %s;"
        data = (tasting_dict['current_grogg_idx'], id)
        cur.execute(sql, data)
        conn.commit()


    if tasting_dict['current_grogg_idx'] >= len(tasting_dict['grogg_list']):
        return redirect(url_for('tasting.result', id=id))
        
    # Extract variables used as input to manage template.
    tasting_name=tasting_dict['tasting_name']
    current_grogg = tasting_dict['grogg_list'][tasting_dict['current_grogg_idx']]
    join_code=tasting_dict['join_code']
    try:
        rated_by = tasting_dict['rated_by'][tasting_dict['current_grogg_idx']]
    except IndexError:
        rated_by = []


    return render_template('tasting/manage.html', tasting_name=tasting_name,
                           current_grogg=current_grogg, join_code=join_code, rated_by=rated_by, tasting_id=id)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':

        tasting_name = request.form['tasting_name']
        grogg_string = request.form['grogg_list']

        error = None

        if len(tasting_name) == 0:
            error = "Namn på provningen krävs!"
        elif len(grogg_string) == 0:
            error = "Groggar krävs!"

        if error is not None:
            flash(error)

        # Split the string with groggs into substring and put in list
        grogg_list = grogg_string.split(';')
        grogg_list = [grogg.rstrip() for grogg in grogg_list]
        grogg_list = [grogg.lstrip() for grogg in grogg_list]

        # Created by
        user_id = g.user['id']
        # Created time
        created = datetime.today().isoformat()
        # Join code
        code = str(random.randint(1, 9999))
        while len(code) < 4: code = '0' + code

        # Establish connection to db
        conn = get_db()
        cur = conn.cursor()
        # Add new tasting to db
        cur.execute("INSERT INTO tastings (tasting_name, created_by, creation_time, join_code, grogg_list) \
                    VALUES (%s, %s, %s, %s, %s) RETURNING id;", (tasting_name, user_id, created, code, grogg_list))

        tasting_id = cur.fetchone()[0]

        conn.commit()

        cur.close()
        # Redirect it to the manage view
        return redirect(url_for('tasting.manage', id=tasting_id))

    return render_template('tasting/create.html')


@bp.route('/join', methods=('GET', 'POST'))
def join():
    if request.method == 'POST':
        join_code = request.form['join_code']
        nickname = request.form['nickname']

        error = None

        if len(join_code) == 0:
            error = "Anslutningskod krävs!"
        elif len(nickname) == 0:
            error = "Smeknamn krävs!"

        if error is not None:
            flash(error)

        # Establish connection to db
        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM tastings WHERE join_code = %s;", (join_code,))
        tasting = cur.fetchone()

        if tasting is None:
            flash("Felaktig anslutningskod.")
        else:
            # Store nickname and id of joined tasting in a new session
            tasting_dict = tasting_entry_as_dict(tasting)
            session.clear()
            session['nickname'] = nickname
            session['joined_tasting'] = tasting_dict['id']
            flash(f"Managed to join tasting {join_code}.")
            return redirect(url_for("tasting.participate", id=tasting_dict['id']))




    return render_template('tasting/join.html')


@bp.route('/<int:id>/result', methods=('GET',))
#TODO: This one next
@login_required
def result(id):
    # Get tasting to manage
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tastings WHERE id=%s;", (id,))
    current_tasting = cur.fetchone()
    tasting_dict = tasting_entry_as_dict(current_tasting)

    ratings = tasting_dict['ratings']

    # Remove potential None ratings
    for l in ratings:
        while l.count([None, None, None]) > 0:
            l.remove([None, None, None])

    avg_ratings = []
    for grogg_ratings in ratings:
        avg_rating = [0, 0, 0, 0]
        for i, rating in enumerate(grogg_ratings):
            avg_rating[0] += rating[0]
            avg_rating[1] += rating[1]
            avg_rating[2] += rating[2]

        avg_rating[0] /= (i+1)
        avg_rating[1] /= (i+1)
        avg_rating[2] /= (i+1)
        avg_rating[3] = (avg_rating[0] + avg_rating[1] + avg_rating[2]) / 3
        avg_ratings.append(avg_rating)

    return render_template('tasting/result.html', tasting_name=tasting_dict['tasting_name'],
                           grogg_list=tasting_dict['grogg_list'], avg_ratings=avg_ratings)



def list_tastings():
    """View that lets a logged in user view the tastings created."""
    raise NotImplementedError