from flask import (
    Blueprint, request, redirect, url_for, render_template, flash, session, g
)
from werkzeug.security import generate_password_hash, check_password_hash
import functools

from grogg_app.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(view):
    """View decorator that redirects anonymous users to login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


def join_required(view):
    """View decorator that redirects un-joined guests to join page."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):

        nickname = session.get('nickname')
        joined_tasting = session.get('joined_tasting')

        if nickname is None or kwargs['id'] != joined_tasting:
            return redirect(url_for('tasting.join'))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
#TODO: Functionality for automatically logging out users after certain time
def load_logged_in_users():
    """If a user id is stored in the session, load the user object from the db
    into ''g.user''."""
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users where id = %s;", (user_id,))
        raw_user = cur.fetchone()
        g.user = {'id':raw_user[0], 'username':raw_user[1]}

        cur.close()


@bp.route('/activate', methods=('GET', 'POST'))
def activate():
    """Allows activation of admin account. Checks that account exists in db
    and is inactivated and that temp password matches. """
    if request.method == "POST":
        username = request.form['username']
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        conn = get_db()
        cur = conn.cursor()
        error = None

        if not username:
            error = "Användarnamn krävs!"
        elif not old_password:
            error = "Gammalt lösenord krävs!"
        elif not new_password:
            error = "Nytt lösenord krävs!"

        if error is None:
            # Everything alright so far
            cur.execute("SELECT * FROM users WHERE username = %s;", (username,))
            user = cur.fetchone()

            if user is None or user[3] or user[2] != old_password:
                error = "Användaren hittades inte, är redan aktiverad eller så är lösenordet felaktigt."

            if error is None:
                # Ready to activate the user
                cur.execute("UPDATE users SET password = %s, activated = TRUE WHERE id = %s;",
                           (generate_password_hash(new_password), user[0])
                )
                conn.commit()
                cur.close()
                return redirect(url_for("auth.login"))

        cur.close()
        flash(error)

    return render_template('auth/activate.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Log in a registered user by adding the user id to the session."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        cur = conn.cursor()
        error = None

        cur.execute("SELECT * FROM users WHERE username = %s;", (username,))
        user = cur.fetchone()

        if user is None:
            error = "Felaktigt användarnamn."
        elif not check_password_hash(user[2], password):
            error = "Felaktigt lösenord."

        if error is None:
            # Store the user id in a new session and return to main page
            session.clear()
            session['user_id'] = user[0]
            return redirect(url_for('start'))

        cur.close()
        flash(error)

    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    """Clear current session, including stored user id:s"""
    session.clear()
    return redirect(url_for('start'))