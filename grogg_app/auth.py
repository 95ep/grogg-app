from flask import (
    Blueprint, request, redirect, url_for, render_template, flash
)

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
# To register as tasting admin. Some check so that not everyone can do this
def register():
    pass

@bp.route('/login', methods=('GET', 'POST'))
def login():
    pass