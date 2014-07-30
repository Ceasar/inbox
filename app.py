from flask import Flask, abort, jsonify

from inbox import make_inbox
from local_settings import USERNAME, PASSWORD


def make_app(username, password):
    app = Flask(__name__)

    app.logger.debug("connecting to inbox...")
    server = make_inbox(username, password)
    app.logger.debug("connected.")

    @app.route('/')
    def index():
        return jsonify({"mailboxes": server.mailboxes})

    @app.route('/<mailbox_name>')
    def show_mailbox(mailbox_name):
        try:
            mailbox = server.get_mailbox(mailbox_name)
        except ValueError:
            abort(404)
        return jsonify({"message_ids": mailbox.get_message_ids()})

    @app.route('/<mailbox_name>/<id>')
    def show_message(mailbox_name, id):
        inbox = server.get_mailbox(mailbox_name)
        email = inbox[-int(id)]
        return jsonify({'headers': email.headers, 'body': email.body})

    return app

if __name__ == "__main__":
    app = make_app(USERNAME, PASSWORD)
    app.run(debug=True, port=8000)
