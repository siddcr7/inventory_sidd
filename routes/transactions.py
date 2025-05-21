from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Item, Transaction
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, TextAreaField, HiddenField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional

transactions_bp = Blueprint('transactions', __name__, url_prefix='/transactions')

class TransactionForm(FlaskForm):
    item_id = SelectField('Item', coerce=int, validators=[DataRequired()])
    quantity_change = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    transaction_type = SelectField('Transaction Type', 
                                  choices=[('addition', 'Add Stock'), ('removal', 'Remove Stock')],
                                  validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Record Transaction')

@transactions_bp.route('/')
def index():
    transactions = Transaction.query.order_by(Transaction.transaction_date.desc()).all()
    return render_template('transactions/index.html', transactions=transactions)

@transactions_bp.route('/add', methods=['GET', 'POST'])
def add():
    form = TransactionForm()
    
    # Get all items for the dropdown
    items = Item.query.all()
    form.item_id.choices = [(item.id, item.name) for item in items]
    
    if form.validate_on_submit():
        item = Item.query.get(form.item_id.data)
        
        # Prepare the quantity change (positive for additions, negative for removals)
        quantity = form.quantity_change.data
        if form.transaction_type.data == 'removal':
            quantity = -quantity
            
            # Check if we have enough stock
            if item.quantity + quantity < 0:
                flash(f'Not enough stock! Current quantity: {item.quantity}', 'danger')
                return render_template('transactions/add.html', form=form)
        
        # Create new transaction
        transaction = Transaction(
            item_id=form.item_id.data,
            quantity_change=quantity,
            transaction_type=form.transaction_type.data,
            notes=form.notes.data
        )
        
        # Update item quantity
        item.quantity += quantity
        item.updated_at = datetime.utcnow()
        
        db.session.add(transaction)
        db.session.commit()
        
        flash('Transaction recorded successfully!', 'success')
        return redirect(url_for('transactions.index'))