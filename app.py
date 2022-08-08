from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import SelectField, FloatField, SubmitField
from wtforms.validators import InputRequired
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = '2389dh01'

compound_list = ['H2', 'C1', 'C2', 'C2H4', 'C3', 'C4', 'iC4', 'C5', 'C6', 'C7', 'C8']
recorded_dict = {}
wtfrac = {}

class Recorder(FlaskForm):
    H2 = FloatField(validators=[InputRequired()])
    C1 = FloatField(validators=[InputRequired()])
    C2 = FloatField(validators=[InputRequired()])
    C2H4 = FloatField(validators=[InputRequired()])
    C3 = FloatField(validators=[InputRequired()])
    C4 = FloatField(validators=[InputRequired()])
    iC4 = FloatField(validators=[InputRequired()])
    C5 = FloatField(validators=[InputRequired()])
    C6 = FloatField(validators=[InputRequired()])
    C7 = FloatField(validators=[InputRequired()])
    C8 = FloatField(validators=[InputRequired()])

    toRecord = SelectField('', choices=compound_list, validators=[InputRequired()])
    Pi = FloatField('Pi', validators=[InputRequired()])
    record = SubmitField('Record')
    reset = SubmitField('Reset')

class RunCalc(FlaskForm):
    vhead = FloatField('Vhead', validators=[InputRequired()])
    mL0 = FloatField('mL0', validators=[InputRequired()])
    temp = FloatField('Temperature', validators=[InputRequired()])
    torun = SelectField('', choices=recorded_dict.keys(), validators=[InputRequired()])
    run = SubmitField('Run')

@app.route('/')
def index():
    recorder = Recorder()
    runcalc = RunCalc()

    sorted_dict = dict(sorted(recorded_dict.items()))

    return render_template('index.html', recorder=recorder, runcalc=runcalc, sorted_dict=sorted_dict, wtfrac=wtfrac,
                           compound_list=compound_list)

@app.route('/record', methods=['POST'])
def record():
    recorder = Recorder()

    if recorder.record.data and recorder.validate():
        recorded_dict.update({recorder.toRecord.data: recorder.Pi.data})

    sorted_dict = dict(sorted(recorded_dict.items()))

    runcalc = RunCalc()

    return render_template('index.html', recorder=recorder, runcalc=runcalc, sorted_dict=sorted_dict, wtfrac=wtfrac,
                           compound_list=compound_list)

@app.route('/reset', methods=['POST'])
def reset():
    recorder = Recorder()

    if recorder.reset.data:
        recorded_dict.clear()

    sorted_dict = dict(sorted(recorded_dict.items()))

    runcalc = RunCalc()

    return render_template('index.html', recorder=recorder, runcalc=runcalc, sorted_dict=sorted_dict, wtfrac=wtfrac,
                           compound_list=compound_list)

@app.route('/calculate', methods=['POST'])
def calculate():
    recorder = Recorder()
    runcalc = RunCalc()

    if runcalc.run.data and runcalc.validate():
        selected = runcalc.torun.data
        with open('compounds.json', 'r') as f:
            summation = 0
            cmpds = json.load(f)

            for i in recorded_dict.keys():
                MWi = cmpds[str(i)]['MW']
                Pi = recorded_dict.get(i)
                vhead = runcalc.vhead.data
                R = 0.08206 # L atm / mol K
                temp = runcalc.temp.data
                mLnought = runcalc.mL0.data
                summation += (MWi * vhead * Pi) / (R * temp * cmpds[selected]['H0'] * mLnought)

            result = 1 / (recorded_dict.get(selected) * ((1 / cmpds[selected]['H0']) - summation + (vhead * cmpds[selected]['MW']) / (R * temp * mLnought)))
            wtfrac.update({selected: result})

    sorted_dict = dict(sorted(recorded_dict.items()))

    return render_template('index.html', recorder=recorder, runcalc=runcalc, sorted_dict=sorted_dict, wtfrac=wtfrac,
                           compound_list=compound_list)

if __name__ == '__main__':
    app.run(debug=True)