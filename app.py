from flask import Flask, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import SelectField, FloatField, SubmitField
from wtforms.validators import InputRequired
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = '2389dh01'

compound_list = ['H2', 'C1', 'C2', 'C2H4', 'C3', 'C4', 'iC4', 'C5', 'C6', 'C7', 'C8']
recorded_dict = {}
wtfrac = {}

class Calculator(FlaskForm):
    H2 = FloatField('H2', validators=[InputRequired()])
    C1 = FloatField('C1', validators=[InputRequired()])
    C2 = FloatField('C2', validators=[InputRequired()])
    C2H4 = FloatField('C2H4', validators=[InputRequired()])
    C3 = FloatField('C3', validators=[InputRequired()])
    C4 = FloatField('C4', validators=[InputRequired()])
    iC4 = FloatField('iC4', validators=[InputRequired()])
    C5 = FloatField('C5', validators=[InputRequired()])
    C6 = FloatField('C6', validators=[InputRequired()])
    C7 = FloatField('C7', validators=[InputRequired()])
    C8 = FloatField('C8', validators=[InputRequired()])

    vhead = FloatField('Vhead', validators=[InputRequired()])
    mL0 = FloatField('mL0', validators=[InputRequired()])
    temp = FloatField('Temperature', validators=[InputRequired()])

    run = SubmitField('Run')
    reset = SubmitField('Reset')

@app.route('/')
def index():
    calculator = Calculator()

    return render_template('index.html', calculator=calculator, wtfrac=wtfrac, compound_list=compound_list)

@app.route('/calculate', methods=['POST'])
def calculate():
    calculator = Calculator()

    if calculator.run.data:
        with open('compounds.json', 'r') as f:
            summation = 0
            cmpds = json.load(f)

            # do summation
            for compound in compound_list:
                MWi = cmpds[str(compound)]['MW']
                vhead = calculator.vhead.data
                Pi = calculator[compound].data
                R = 0.08206 # L atm / mol K
                temp = calculator.temp.data
                mLnought = calculator.mL0.data
                summation += MWi * vhead * Pi

            # do wt frac calculation
            for compound in compound_list:
                H0 = cmpds[compound]['H0']
                local_summation = summation / (R * temp * H0 * mLnought)
                try:
                    result = 1 / (calculator[compound].data * ((1 / H0) - local_summation + (vhead * cmpds[compound]['MW']) / (R * temp * mLnought)))
                except ZeroDivisionError:
                    result = 0
                wtfrac.update({compound: result})

    return render_template('index.html', calculator=calculator, wtfrac=wtfrac, compound_list=compound_list)

@app.route('/reset', methods=['POST'])
def reset():
    calculator = Calculator()

    if calculator.reset.data:
        wtfrac.clear()
        return render_template('index.html', calculator=calculator, wtfrac=wtfrac, compound_list=compound_list)

if __name__ == '__main__':
    app.run(debug=True)