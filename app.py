from flask import Flask, abort, jsonify, url_for

from inbox import AuthenticationError, Server
from local_settings import USERNAME, PASSWORD


def make_app(username, password):
    app = Flask(__name__)

    app.logger.debug("connecting to inbox...")
    server = Server("imap.gmail.com", username, password)
    app.logger.debug("connected.")

    @app.route('/')
    def index():
        try:
            mailboxes = server.connect().list()
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
            mailbox = server.connect().select(mailbox_name)
        except AuthenticationError:
            abort(401)
        except ValueError:
            abort(404)
        message_ids = mailbox.list_messages()
        resp = {
            "name": mailbox_name,
            "messages": [url_for('show_message', mailbox_name=mailbox_name,
                                 id=id, _external=True) for id in message_ids],
        }
        return jsonify(resp)

    @app.route('/<path:mailbox_name>/<int:id>')
    def show_message(mailbox_name, id):
        try:
            inbox = server.connect().select(mailbox_name)
        except AuthenticationError:
            abort(401)
        email = inbox[-int(id)]
        return jsonify({'headers': email.headers, 'body': email.body})

    return app

if __name__ == "__main__":
    app = make_app(USERNAME, PASSWORD)
    app.run(debug=True, port=8000)
