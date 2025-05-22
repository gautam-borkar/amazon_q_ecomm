from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models.product import Product
import os
import uuid

products = Blueprint('products', __name__)

@products.route('/products')
def product_list():
    page = request.args.get('page', 1, type=int)
    products = Product.query.paginate(page=page, per_page=12)
    return render_template('products/product_list.html', products=products)

@products.route('/products/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('products/product_detail.html', product=product)

# Admin routes for product management (in a real app, add admin role check)
@products.route('/admin/products')
@login_required
def admin_products():
    products = Product.query.all()
    return render_template('admin/products.html', products=products)

@products.route('/admin/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        image = request.files.get('image')
        
        # Save image if provided
        image_filename = None
        if image and image.filename:
            # Generate unique filename
            filename = secure_filename(image.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            
            # Save file
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            image.save(image_path)
            image_filename = unique_filename
        
        # Create new product
        new_product = Product(
            name=name,
            description=description,
            price=float(price),
            image_filename=image_filename
        )
        
        db.session.add(new_product)
        db.session.commit()
        
        flash('Product added successfully')
        return redirect(url_for('products.admin_products'))
    
    return render_template('admin/add_product.html')

@products.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = float(request.form.get('price'))
        
        # Handle image update
        image = request.files.get('image')
        if image and image.filename:
            # Delete old image if exists
            if product.image_filename:
                old_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], product.image_filename)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            
            # Save new image
            filename = secure_filename(image.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            image.save(image_path)
            product.image_filename = unique_filename
        
        db.session.commit()
        flash('Product updated successfully')
        return redirect(url_for('products.admin_products'))
    
    return render_template('admin/edit_product.html', product=product)