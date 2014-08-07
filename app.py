from flask import Flask, abort, jsonify, url_for

from imaplib2 import Server
from local_settings import USERNAME, PASSWORD


def create_app(conn):
    app = Flask(__name__)

    @app.route('/')
    def index():
        mailboxes = conn.list()
        resp = {"mailboxes": [
            url_for('show_mailbox', mailbox_name=mailbox.name,
                    _external=True)
            for mailbox in mailboxes
        ]}
        return jsonify(resp)

    @app.route('/<path:mailbox_name>')
    def show_mailbox(mailbox_name):
        try:
            with conn.select(mailbox_name) as mailbox:
                resp = {
                    "name": mailbox_name,
                    "messages": [
                        url_for('show_message', mailbox_name=mailbox_name,
                                uid=message_uid, _external=True)
                        for message_uid in mailbox
                    ],
                }
                return jsonify(resp)
        except ValueError:
            abort(404)

    @app.route('/<path:mailbox_name>/<int:uid>')
    def show_message(mailbox_name, uid):
        try:
            with conn.select(mailbox_name) as mailbox:
                email = mailbox.fetch(int(uid))
                return jsonify({'headers': email.headers, 'body': email.body})
        except ValueError:
            abort(404)

    @app.route('/<path:mailbox_name>/<int:uid>/raw')
    def show_raw_message(mailbox_name, uid):
        try:
            with conn.select(mailbox_name) as mailbox:
                email = mailbox.fetch(int(uid))
                return jsonify({'raw': email.raw})
        except ValueError:
            abort(404)

    return app

if __name__ == "__main__":
    with Server("imap.gmail.com").connect(USERNAME, PASSWORD) as conn:
        app = create_app(conn)
        app.run(debug=True, port=8000)
