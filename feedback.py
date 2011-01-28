# -*- coding: utf-8 -*-
"""
    Flask Feedback
    ~~~~~~~~~~~~~~

    We want to know what where we should improve.  This website should
    help us achieve that goal.

    Inspired by what the Mozilla guys did for Firefox.

    :copyright: (c) Copyright 2011 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

from datetime import datetime
from random import SystemRandom
from flask import Flask, render_template, session, request, \
     url_for, redirect, Response, jsonify
from flaskext.sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['FEEDBACK_PER_PAGE'] = 30
app.config.from_pyfile('settings.cfg')
db = SQLAlchemy(app)
rnd = SystemRandom()


class Feedback(db.Model):
    id = db.Column('feedback_id', db.Integer, primary_key=True)
    kind = db.Column(db.Integer)
    text = db.Column(db.String(1000))
    version = db.Column(db.String(40))
    pub_date = db.Column(db.DateTime)

    UNHAPPY = -1
    HAPPY = 1
    KINDS = {'unhappy': UNHAPPY, 'happy': HAPPY}

    def __init__(self, kind, text, version):
        assert kind in (self.UNHAPPY, self.HAPPY)
        self.kind = kind
        self.text = text
        self.version = version
        self.pub_date = datetime.utcnow()

    @property
    def kind_symbol(self):
        if self.kind == self.HAPPY:
            return '+'
        elif self.kind == self.UNHAPPY:
            return '-'
        return '?'

    def to_json(self):
        return {
            'kind':     self.kind_symbol,
            'text':     self.text,
            'version':  self.version,
            'pub_date': self.pub_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        }


def show_feedback(kind, page):
    """Renders returned feedback."""
    pagination = Feedback.query \
        .filter_by(kind=Feedback.KINDS[kind]) \
        .order_by(Feedback.pub_date.desc()) \
        .paginate(page, app.config['FEEDBACK_PER_PAGE'])
    return render_template('show_feedback.html', kind=kind,
                           pagination=pagination)


def get_challenge():
    """Return a random challenge"""
    return rnd.randrange(1 << 32)


def challenge_response_accepted(challenge, response):
    """Simple check if a valid response for the challenge was provided."""
    try:
        response = int(response)
    except ValueError:
        return False
    expected = int((challenge / 2.0) + (challenge / 3.0) - (challenge / 4.0))
    return expected == response


@app.route('/', methods=['GET', 'POST'])
def give_feedback():
    if request.method == 'POST':
        challenge = session.pop('challenge', None)
        kind = Feedback.KINDS.get(request.form['kind'])
        text = request.form['feedback']
        version = request.form['version']
        if challenge and challenge_response_accepted(
                challenge, request.form['response']) and \
           kind is not None and len(text) <= 140 and len(version) <= 20:
            feedback = Feedback(kind, text, version)
            db.session.add(feedback)
            db.session.commit()
            return redirect(url_for('show_message', id=feedback.id))
        return redirect(url_for('give_feedback'))
    session['challenge'] = challenge = get_challenge()
    return render_template('give_feedback.html', challenge=challenge)


@app.route('/message/<int:id>')
def show_message(id):
    feedback = Feedback.query.get_or_404(id)
    return render_template('show_message.html', feedback=feedback)


@app.route('/happy', defaults={'page': 1})
@app.route('/happy/page/<int:page>')
def happy(page):
    return show_feedback('happy', page)


@app.route('/unhappy', defaults={'page': 1})
@app.route('/unhappy/page/<int:page>')
def unhappy(page):
    return show_feedback('unhappy', page)


@app.route('/faq')
def faq():
    return render_template('faq.html')


@app.route('/feedback.txt', defaults={'version': 'all'})
@app.route('/feedback-<version>.txt')
def export_text(version):
    q = Feedback.query
    if version != 'all':
        q = q.filter_by(version=version)
    messages = q.order_by(Feedback.pub_date).all()
    return Response(u'\n'.join('[%s] %s: %s (Flask-%s)' % (
        fb.kind_symbol,
        fb.pub_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
        fb.text,
        fb.version or 'unknown'
    ) for fb in messages), mimetype='text/plain')


@app.route('/feedback.json', defaults={'version': 'all'})
@app.route('/feedback-<version>.json')
def export_json(version):
    q = Feedback.query
    if version != 'all':
        q = q.filter_by(version=version)
    messages = q.order_by(Feedback.pub_date).all()
    return jsonify(messages=[fb.to_json() for fb in messages])
