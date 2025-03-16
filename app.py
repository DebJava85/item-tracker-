from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///info.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

# Info Model
class Info(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    details = db.Column(db.String(200), nullable=False)

# Form for creating and editing entries
class InfoForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    details = StringField('Details', validators=[DataRequired()])

@app.route('/')
def home():
    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = 6  # Number of cards per page

    if search_query:
        items = Info.query.filter(
            Info.name.contains(search_query) | Info.details.contains(search_query)
        ).paginate(page=page, per_page=per_page)
    else:
        items = Info.query.paginate(page=page, per_page=per_page)

    return render_template('home.html', items=items, search_query=search_query)

@app.route('/create', methods=['GET', 'POST'])
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def create_edit(id=None):
    form = InfoForm()
    info = None
    if id:
        info = Info.query.get_or_404(id)
        if request.method == 'POST' and form.validate_on_submit():
            info.name = form.name.data
            info.details = form.details.data
            db.session.commit()
            flash('Information updated successfully!', 'success')
            return redirect(url_for('home'))
    else:
        if request.method == 'POST' and form.validate_on_submit():
            new_info = Info(name=form.name.data, details=form.details.data)
            db.session.add(new_info)
            db.session.commit()
            flash('Information saved successfully!', 'success')
            return redirect(url_for('home'))

    return render_template('create_edit.html', form=form, info=info)

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    info = Info.query.get_or_404(id)
    db.session.delete(info)
    db.session.commit()
    flash('Information deleted successfully!', 'danger')
    return redirect(url_for('home'))

if __name__ == '__main__':
    db.create_all()  # Create database and tables
    app.run(debug=True)