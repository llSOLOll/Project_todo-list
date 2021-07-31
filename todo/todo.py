from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from todo.auth import login_required
from todo.db import get_db

bp = Blueprint('todo', __name__)



@bp.route('/')
def index():
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        'SELECT p.id, title, body, created, author_id, username, due, status'
        ' FROM data p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    )
    posts = cursor.fetchall()

    return render_template('main/index.html', posts=posts)



@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        due_date = request.form['date']
        due_time = request.form['time']
        due = str(due_date + ' ' + due_time +':00')

        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO data (title, body, due, author_id)'
                ' VALUES (?, ?, ?, ?)',
                (title, body, due, g.user['id'])
            )
            db.commit()
            return redirect(url_for('index'))

    return render_template('main/create.html')




def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM data p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post




@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        due_date = request.form['date']
        due_time = request.form['time']
        due = str(due_date + ' ' + due_time +':00')
        status = request.form.get('status_select')

        error = None

        if not title:
            error = 'Title is required.'

        if not due:
            error = 'Due time is required'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE data SET title = ?, body = ?, due = ?, status = ?'
                ' WHERE id = ?',
                (title, body, due, status, id)
            )
            db.commit()
            return redirect(url_for('index'))

    return render_template('main/update.html', post=post)






@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM data WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('index'))