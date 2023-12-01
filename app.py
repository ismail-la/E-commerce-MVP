from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import paypalrestsdk  # Add this line

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://ismail:pass@localhost/db_ismail'
app.config['SECRET_KEY_367UHDDG'] = 'your_secret_key'  # Change this to a secure random key
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User model, login setup, Product model, product management, and shopping cart (previous sections)...

# PayPal Integration
paypal_mode = 'sandbox'  # Change to 'live' for production
paypal_client_id = 'your_paypal_client_id'
paypal_client_secret = 'your_paypal_client_secret'

paypal_api = paypalrestsdk.configure({
    'mode': paypal_mode,
    'client_id': paypal_client_id,
    'client_secret': paypal_client_secret
})

@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    if 'cart' not in session or not session['cart']:
        return redirect(url_for('cart'))

    items = []
    total_price = 0

    for product_id in session['cart']:
        product = Product.query.get(product_id)
        if product:
            items.append({
                'name': product.name,
                'sku': str(product.id),
                'price': f'{product.price:.2f}',
                'currency': 'USD',
                'quantity': 1
            })
            total_price += product.price

    payment_data = {
        'intent': 'sale',
        'payer': {'payment_method': 'paypal'},
        'redirect_urls': {
            'return_url': url_for('success', _external=True),
            'cancel_url': url_for('cart')
        },
        'transactions': [{
            'item_list': {'items': items},
            'amount': {'total': f'{total_price:.2f}', 'currency': 'USD'},
            'description': 'E-commerce Purchase'
        }]
    }

    payment = Payment(payment_data)

    if payment.create():
        return redirect(payment.links[1].href)
    else:
        return f'Error creating payment: {payment.error}'

@app.route('/success')
@login_required
def success():
    session.pop('cart', None)  # Clear the cart after successful payment
    return 'Payment successful!'

if __name__ == '__main__':
    app.run(debug=True)
