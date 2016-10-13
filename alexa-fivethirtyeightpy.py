import logging
from flask import Flask, render_template
from flask_ask import Ask, statement, question
from pyvethirtyeight import FiveThirtyEight

app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger("alexa-fivethirtyeight").setLevel(logging.DEBUG)

candidate_names = {
    'clinton': 'hillary clinton',
    'trump': 'donald trump',
    'johnson': 'gary johnson',
    'stein': 'jill stein'
}


@ask.launch
def start():
    welcome_msg = render_template('welcome')
    help_msg = render_template('help')
    return question(welcome_msg).reprompt(help_msg)


@ask.intent("OneShotLeaderIntent")
def one_shot_leader():
    leader_forecast = FiveThirtyEight().current_leader()
    winprob = leader_forecast.models['polls']['winprob']
    candidate_full_name = candidate_names[leader_forecast.candidate.lower()]
    leader_msg = render_template('leader_winprob',
                                 candidate=candidate_full_name,
                                 winprob=winprob)
    return statement(leader_msg)


@ask.intent("OneShotCandidateIntent",
            mapping={'candidate': 'Candidate'})
def one_shot_candidate(candidate):
    forecasts = FiveThirtyEight().latest_forecasts()
    winprob = 0
    for f in forecasts:
        if f.candidate.lower() == candidate.split()[-1].lower():
            winprob = f.models['polls']['winprob']
            break
    else:
        return statement(render_template('no_data_on_candidate',
                                         candidate=candidate))
    candidate_msg = render_template('candidate_winprob',
                                    candidate=candidate,
                                    percentage=winprob)
    return statement(candidate_msg)

if __name__ == '__main__':
    app.run(debug=True)
