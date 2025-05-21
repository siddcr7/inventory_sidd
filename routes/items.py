from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Item, Transaction
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional

items_bp = Blueprint('items', __name__, url_prefix='/items')

class ItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    quantity = IntegerField('Quantity', validators=[NumberRange(min=0)], default=0)
    min_quantity = IntegerField('Minimum Quantity', validators=[NumberRange(min=0)], default=5)
    price = FloatField('Price', validators=[NumberRange(min=0)], default=0.0)
    category = StringField('Category', validators=[Optional()])
    sku = StringField('SKU', validators=[Optional()])
    location = StringField('Storage Location', validators=[Optional()])
    submit = SubmitField('Save Item')

@items_bp.route('/')
def index():
    items = Item.query.all()
    return render_template('items/index.html', items=items)

@items_bp.route('/add', methods=['GET', 'POST'])
def add():
    form = ItemForm()
    
    if form.validate_on_submit():
        item = Item(
            name=form.name.data,
            description=form.description.data,
            quantity=form.quantity.data,
            min_quantity=form.min_quantity.data,
            price=form.price.data,
            category=form.category.data,
            sku=form.sku.data,
            location=form.location.data
        )
        
        db.session.add(item)
        db.session.commit()
        
        # Create initial transaction if quantity > 0
        if form.quantity.data > 0:
            transaction = Transaction(
                item_id=item.id,
                quantity_change=form.quantity.data,
                transaction_type='addition',
                notes='Initial inventory'
            )
            db.session.add(transaction)
            db.session.commit()
            
        flash('Item added successfully!', 'success')
        return redirect(url_for('items.index'))
    
    return render_template('items/add.html', form=form)

@items_bp.route('/<int:item_id>')
def view(item_id):
    item = Item.query.get_or_404(item_id)
    transactions = Transaction.query.filter_by(item_id=item_id).order_by(Transaction.transaction_date.desc()).all()
    return render_template('items/view.html', item=item, transactions=transactions)

@items_bp.route('/<int:item_id>/edit', methods=['GET', 'POST'])
def edit(item_id):
    item = Item.query.get_or_404(item_id)
    form = ItemForm(obj=item)
    
    if form.validate_on_submit():
        # Save original quantity to track changes
        original_quantity = item.quantity
        
        # Update item with form data
        form.populate_obj(item)
        
        # Calculate quantity change
        quantity_change = item.quantity - original_quantity
        
        db.session.commit()
        
        # Create transaction for quantity adjustment if needed
        if quantity_change != 0:
            transaction = Transaction(
                item_id=item.id,
                quantity_change=quantity_change,
                transaction_type='adjustment',
                notes=f'Quantity adjusted during item edit'
            )
            db.session.add(transaction)
            db.session.commit()
            
        flash('Item updated successfully!', 'success')
        return redirect(url_for('items.view', item_id=item.id))
    
    return render_template('items/edit.html', form=form, item=item)

@items_bp.route('/<int:item_id>/delete', methods=['POST'])
def delete(item_id):
    item = Item.query.get_or_404(item_id)
    
    # Delete related transactions first (to avoid foreign key constraint)
    Transaction.query.filter_by(item_id=item_id).delete()
    
    db.session.delete(item)
    db.session.commit()
    
    flash('Item deleted successfully!', 'success')
    return redirect(url_for('items.index'))