from flask import Flask, abort, jsonify

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
            return jsonify({"mailboxes": server.connect().list_mailboxes()})
        except AuthenticationError:
            abort(401)

    @app.route('/<mailbox_name>')
    def show_mailbox(mailbox_name):
        try:
            mailbox = server.connect().get_mailbox(mailbox_name)
        except AuthenticationError:
            abort(401)
        except ValueError:
            abort(404)
        return jsonify({"message_ids": mailbox.list_messages()})

    @app.route('/<mailbox_name>/<id>')
    def show_message(mailbox_name, id):
        try:
            inbox = server.connect().get_mailbox(mailbox_name)
        except AuthenticationError:
            abort(401)
        email = inbox[-int(id)]
        return jsonify({'headers': email.headers, 'body': email.body})

    return app

if __name__ == "__main__":
    app = make_app(USERNAME, PASSWORD)
    app.run(debug=True, port=8000)
