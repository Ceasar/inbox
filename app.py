from flask import Flask, jsonify

from inbox import make_inbox

from local_settings import USERNAME, PASSWORD


def make_app():
    app = Flask(__name__)
    inbox = make_inbox(USERNAME, PASSWORD)

    @app.route('/<id>')
    def show_email(id):
        email = inbox[-int(id)]
        return jsonify({'headers': email.headers, 'body': email.body})

    return app

if __name__ == "__main__":
    app = make_app()
    app.run(debug=True)
