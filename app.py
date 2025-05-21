from flask import Flask, render_template
from flask_migrate import Migrate
from config import Config
from models import db, Item, Transaction
from routes.items import items_bp
from routes.transactions import transactions_bp
import os

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize database
    db.init_app(app)
    
    # Initialize migrations
    migrate = Migrate(app, db)
    
    # Register blueprints
    app.register_blueprint(items_bp)
    app.register_blueprint(transactions_bp)
    
    # Root route
    @app.route('/')
    def index():
        low_stock_count = Item.query.filter(Item.quantity <= Item.min_quantity).count()
        total_items = Item.query.count()
        total_value = sum(item.quantity * item.price for item in Item.query.all())
        recent_transactions = Transaction.query.order_by(Transaction.transaction_date.desc()).limit(5).all()
        
        return render_template('index.html', 
                              low_stock_count=low_stock_count,
                              total_items=total_items,
                              total_value=total_value,
                              recent_transactions=recent_transactions)
    
    # Low stock report
    @app.route('/reports/low-stock')
    def low_stock_report():
        low_stock_items = Item.query.filter(Item.quantity <= Item.min_quantity).all()
        return render_template('reports/low_stock.html', items=low_stock_items)
    
    return app

# For direct execution
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)