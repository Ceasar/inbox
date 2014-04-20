from flask import Flask, jsonify

from inbox import make_inbox

from local_settings import USERNAME, PASSWORD


def make_app(inbox):
    app = Flask(__name__)

    @app.route('/<id>')
    def show_email(id):
        email = inbox[-int(id)]
        return jsonify({'headers': email.headers, 'body': email.body})

    return app

if __name__ == "__main__":
    inbox = make_inbox(USERNAME, PASSWORD)
    app = make_app(inbox)
    app.run(debug=True)
