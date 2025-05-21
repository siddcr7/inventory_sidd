from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Item(db.Model):
    """Inventory item model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    quantity = db.Column(db.Integer, default=0)
    min_quantity = db.Column(db.Integer, default=5)  # Minimum stock level
    price = db.Column(db.Float, default=0.0)
    category = db.Column(db.String(50), nullable=True)
    sku = db.Column(db.String(50), unique=True, nullable=True)
    location = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    transactions = db.relationship('Transaction', backref='item', lazy=True)
    
    def __repr__(self):
        return f'<Item {self.name}>'
    
    @property
    def is_low_stock(self):
        """Check if item is below minimum quantity"""
        return self.quantity <= self.min_quantity


class Transaction(db.Model):
    """Inventory transaction model for tracking stock changes"""
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantity_change = db.Column(db.Integer, nullable=False)  # Positive for additions, negative for removals
    transaction_type = db.Column(db.String(20), nullable=False)  # 'addition', 'removal', 'adjustment'
    notes = db.Column(db.Text, nullable=True)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Transaction {self.id} - {self.transaction_type}>'