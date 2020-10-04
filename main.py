import os

from flask import Flask, render_template, request, redirect, url_for, session

from model import Donation, Donor

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY').encode()


@app.route('/')
def home():
    return redirect(url_for('all'))


@app.route('/donations/')
def all():
    donations = Donation.select()
    return render_template('donations.jinja2', donations=donations)


@app.route('/create/', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        value = request.form['donation']
        try:
            donor = Donor.select().where(Donor.name == request.form['name']).get()
        except Donor.DoesNotExist:
            session['new_donor'] = request.form['name']
            session['value'] = value
            return redirect(url_for('confirm'))
        new_donation = Donation(value=value, donor=donor)
        new_donation.save()
        return redirect(url_for('all'))
    else:
        return render_template('create.jinja2')


@app.route('/confirm/', methods=['GET', 'POST'])
def confirm():
    if request.method == 'POST':
        if 'yes' in request.form:
            new_donor = Donor(name=session['new_donor'])
            new_donor.save()
            new_donation = Donation(value=session['value'], donor=new_donor)
            new_donation.save()
            session['new_donor'] = None
            session['value'] = None
            return redirect(url_for('all'))
        else:
            session['new_donor'] = None
            session['value'] = None
            return redirect(url_for('create'))
    elif session['new_donor']:
        return render_template('confirm_donor.jinja2', donor_name=session['new_donor'], value=session['value'])
    else:
        return redirect(url_for('all'))


@app.route('/select_single/', methods=['GET', 'POST'])
def select_single():
    if request.method == 'POST':
        donor = Donor.select().where(Donor.name == request.form['name']).get()
        donations = Donation.select().join(Donor).where(Donor.name == donor.name)
        return render_template('view_single.jinja2', donor=donor, donations=donations)
    else:
        return render_template('select_single.jinja2', donors=Donor.select())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 6738))
    app.run(host='0.0.0.0', port=port)
