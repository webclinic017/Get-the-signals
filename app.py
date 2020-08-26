from SV import app, db
from flask import render_template, redirect, request, url_for, flash, abort
from flask_login import login_user, login_required, logout_user
from SV.models import User
from SV.forms import LoginForm, RegistrationForm
from werkzeug.security import generate_password_hash, check_password_hash

from SV.sqlite_utils import from_csv_to_sqlite3
from bokeh.util.string import encode_utf8
from bokeh.resources import INLINE
from bokeh.models import DataRange1d
from bokeh.embed import components
from bokeh.models import ColumnDataSource, CustomJS, Slider
from bokeh.layouts import column
from bokeh.plotting import figure, output_file, show

import sqlite3


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/welcome')
@login_required
def welcome_user():
    return render_template('welcome_user.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You logged out!')
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()
    if form.validate_on_submit():
        # Grab the user from our User Models table
        user = User.query.filter_by(email=form.email.data).first()

        # Check that the user was supplied and the password is right
        # The verify_password method comes from the User object
        # https://stackoverflow.com/questions/2209755/python-operation-vs-is-not

        if user.check_password(form.password.data) and user is not None:
            # Log in the user

            login_user(user)
            flash('Logged in successfully.')

            # If a user was trying to visit a page that requires a login
            # flask saves that URL as 'next'.
            next = request.args.get('next')

            # So let's now check if that next exists, otherwise we'll go to
            # the welcome page.
            if next == None or not next[0] == '/':
                next = url_for('welcome_user')

            return redirect(next)
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)

        db.session.add(user)
        db.session.commit()
        flash('Thanks for registering! Now you can login!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/graph')
@login_required
def graph():
    x = [x*0.005 for x in range(0, 200)]
    y = x

    source = ColumnDataSource(data=dict(x=x, y=y))

    plot = figure(plot_width=400, plot_height=400)
    plot.line('x', 'y', source=source, line_width=3, line_alpha=0.6)

    callback = CustomJS(args=dict(source=source), code="""
            var data = source.data;
            var f = cb_obj.value
            var x = data['x']
            var y = data['y']
            for (var i = 0; i < x.length; i++) {
                y[i] = Math.pow(x[i], f)
            }
            source.change.emit();
        """)

    slider = Slider(start=0.1, end=4, value=1, step=.1, title="power")
    slider.js_on_change('value', callback)

    layout = column(slider, plot)
    script, (plot_div, slider_div) = components((plot, column(slider)))
    kwargs = {'script': script, 'plot_div': plot_div, 'slider_div': slider_div}
    kwargs['title'] = 'bokeh-with-flask'

    return render_template('graph.html', **kwargs)


@app.route('/multiple')
@login_required
def multiple():
    title = 'multiple'
    from bokeh.plotting import figure

    # First Plot
    p = figure(plot_width=400, plot_height=400)
    p.circle([1, 2, 3, 4, 5], [6, 7, 2, 4, 5],
             size=20, color="navy", alpha=0.5)

    # Second Plot
    p2 = figure(plot_width=400, plot_height=400)
    p2.square([5, 8, 3, 4, 5], [20, 7, 2, 1, 25],
              size=20, color="red", alpha=0.5)

    script, div = components(p)
    script2, div2 = components(p2)

    return render_template('multiple.html', title=title, script=script,
                           div=div, script2=script2, div2=div2)


@app.route('/table')
@login_required
def table():
    def fetch():
        conn = sqlite3.connect("US_STOCKS.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT TICKER, SECTOR, PRICE, INDUSTRY, VOLUME FROM OVERVIEW")
        items = cursor.fetchmany(50)
        return items
        # simply to have a proposer display without commas and parantheses specific to tuple format
        # items = [item[0] for item in items]

    try:
        items = fetch()
    except sqlite3.OperationalError:
        from_csv_to_sqlite3()
        items = fetch()

    return render_template('table.html', items=items)


if __name__ == '__main__':
    app.run(debug=True)
