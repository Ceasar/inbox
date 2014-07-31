from flask import Flask, abort, jsonify, url_for

from imaplib2 import Server
from imaplib2.exc import AuthenticationError
from local_settings import USERNAME, PASSWORD


def make_app(conn):
    app = Flask(__name__)

    @app.route('/')
    def index():
        try:
            mailboxes = conn.list()
            resp = {"mailboxes": [
                url_for('show_mailbox', mailbox_name=mailbox.name,
                        _external=True)
                for mailbox in mailboxes
            ]}
            return jsonify(resp)
        except AuthenticationError:
            abort(401)

    @app.route('/<path:mailbox_name>')
    def show_mailbox(mailbox_name):
        try:
            mailbox = conn.select(mailbox_name)
        except AuthenticationError:
            abort(401)
        except ValueError:
            abort(404)
        resp = {
            "name": mailbox_name,
            "messages": [
                url_for('show_message', mailbox_name=mailbox_name,
                        id=message_id, _external=True)
                for message_id in mailbox
            ],
        }
        return jsonify(resp)

    @app.route('/<path:mailbox_name>/<int:id>')
    def show_message(mailbox_name, id):
        try:
            mailbox = conn.select(mailbox_name)
        except AuthenticationError:
            abort(401)
        email = mailbox.fetch(int(id))
        return jsonify({'headers': email.headers, 'body': email.body})

    return app

if __name__ == "__main__":
    with Server("imap.gmail.com").connect(USERNAME, PASSWORD) as conn:
        app = make_app(conn)
        app.run(debug=True, port=8000)
