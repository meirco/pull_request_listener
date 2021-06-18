from flask import Flask, request, json
from flask_cors import CORS
from github import Github
from secrets_cheat import GITHUB_KEY, GIT_SECRET
from flask_sqlalchemy import SQLAlchemy


access_key = GITHUB_KEY
git_secret = GIT_SECRET

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = git_secret
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pulls.db'
app.config['CORS_HEADERS'] = 'Content-Type'

db = SQLAlchemy(app)


def enter_git(key):
    git = Github(key)
    user = git.get_user()
    repos = user.get_repos()

    return user, repos


class PullsDetails(db.Model):
    action = db.Column(db.String(200), nullable=False)
    number = db.Column(db.Integer)
    pull_request = db.Column(db.String(50000))
    repository = db.Column(db.String(50000))
    sender = db.Column(db.String(200))
    raw_data = db.Column(db.String(5000000), primary_key=True)

    def __repr__(self):
        return '<Task %r>' % self.user


# getting a pull request details from Github
@app.route('/github', methods=['POST'])
def api_gh_msg():
    if request.headers['Content-Type'] == 'application/json':
        a_json = request.json
        print(a_json)

        pull = PullsDetails(action=a_json['action'], number=a_json['number'],
                            pull_request=json.dumps(a_json['pull_request']),
                            repository=json.dumps(a_json['repository']), sender=json.dumps(a_json['sender']),
                            raw_data=json.dumps(a_json))

        db.session.add(pull)
        db.session.commit()

        return a_json


# sending the pull request details to client in http://localhost:3000/.
@app.route("/pulldata", methods=['GET'])
def table():
    data_query = PullsDetails.query.all()[0]
    data = {"action": data_query.action,
            "number": str(data_query.number),
            "pull_request": data_query.pull_request,
            "repository": data_query.repository,
            "sender": data_query.sender,
            "raw_data": data_query.raw_data}
    return data


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
