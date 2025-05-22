from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models.product import Product
from app.models.cart import CartItem
from app.models.order import Order, OrderItem
import os

cart = Blueprint('cart', __name__)

@cart.route('/cart')
@login_required
def view_cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('cart/cart.html', cart_items=cart_items, total=total)

@cart.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))
    
    # Check if product already in cart
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if cart_item:
        # Update quantity
        cart_item.quantity += quantity
    else:
        # Add new item to cart
        cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)
    
    db.session.commit()
    flash(f'{product.name} added to cart')
    
    return redirect(url_for('products.product_detail', product_id=product_id))

@cart.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    
    # Ensure the cart item belongs to the current user
    if cart_item.user_id != current_user.id:
        flash('Unauthorized action')
        return redirect(url_for('cart.view_cart'))
    
    quantity = int(request.form.get('quantity', 1))
    
    if quantity > 0:
        cart_item.quantity = quantity
        db.session.commit()
    else:
        db.session.delete(cart_item)
        db.session.commit()
    
    return redirect(url_for('cart.view_cart'))

@cart.route('/cart/remove/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    
    # Ensure the cart item belongs to the current user
    if cart_item.user_id != current_user.id:
        flash('Unauthorized action')
        return redirect(url_for('cart.view_cart'))
    
    db.session.delete(cart_item)
    db.session.commit()
    flash('Item removed from cart')
    
    return redirect(url_for('cart.view_cart'))

@cart.route('/checkout')
@login_required
def checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        flash('Your cart is empty')
        return redirect(url_for('cart.view_cart'))
    
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('cart/checkout.html', cart_items=cart_items, total=total)

@cart.route('/payment', methods=['POST'])
@login_required
def payment():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        flash('Your cart is empty')
        return redirect(url_for('cart.view_cart'))
    
    total = sum(item.product.price * item.quantity for item in cart_items)
    
    # Create a new order
    order = Order(
        user_id=current_user.id,
        total_amount=total,
        status='pending'
    )
    db.session.add(order)
    db.session.commit()
    
    # Add order items
    for cart_item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            price=cart_item.product.price
        )
        db.session.add(order_item)
    
    db.session.commit()
    
    # Simulate successful payment
    return redirect(url_for('cart.payment_success', order_id=order.id))

@cart.route('/payment/success/<int:order_id>')
@login_required
def payment_success(order_id):
    order = Order.query.get_or_404(order_id)
    
    # Ensure the order belongs to the current user
    if order.user_id != current_user.id:
        flash('Unauthorized action')
        return redirect(url_for('main.index'))
    
    # Update order status
    order.status = 'completed'
    db.session.commit()
    
    # Clear the cart
    CartItem.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    
    flash('Payment successful! Your order has been placed.')
    return render_template('cart/payment_success.html', order=order)

@cart.route('/payment/cancel/<int:order_id>')
@login_required
def payment_cancel(order_id):
    order = Order.query.get_or_404(order_id)
    
    # Ensure the order belongs to the current user
    if order.user_id != current_user.id:
        flash('Unauthorized action')
        return redirect(url_for('main.index'))
    
    # Update order status
    order.status = 'cancelled'
    db.session.commit()
    
    flash('Payment cancelled. Your order has not been processed.')
    return redirect(url_for('cart.view_cart'))