"""
Catalog routes.

Defines the catalog_bp Blueprint and handles browsing, creating, editing,
and deleting items, plus JSON API endpoints.

All write operations require the user to be logged in (login_required).
Edit and delete additionally verify that the requesting user owns the item.
"""

from flask import (
    Blueprint,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from sqlalchemy import desc

from auth import login_required
from database import db_session
from models import Category, Item

catalog_bp = Blueprint("catalog", __name__)


# ---------- Read ----------


@catalog_bp.route("/")
@catalog_bp.route("/catalog")
def show_catalog():
    """
    Homepage: all categories in the sidebar, ten most-recently added items
    on the right.  Logged-in users also see an 'Add Item' button.
    """
    categories = db_session.query(Category).order_by(Category.name).all()
    latest_items = db_session.query(Item).order_by(desc(Item.id)).limit(10).all()
    return render_template(
        "catalog.html",
        categories=categories,
        latest_items=latest_items,
    )


@catalog_bp.route("/catalog/<string:category_name>/items")
def show_category(category_name):
    """List all items that belong to the given category."""
    categories = db_session.query(Category).order_by(Category.name).all()
    category = db_session.query(Category).filter_by(name=category_name).first()
    if not category:
        abort(404)
    items = db_session.query(Item).filter_by(category_id=category.id).all()
    return render_template(
        "category.html",
        categories=categories,
        category=category,
        items=items,
    )


@catalog_bp.route("/catalog/<string:category_name>/<string:item_name>")
def show_item(category_name, item_name):
    """
    Show the detail page for one item.

    Edit and Delete links are only shown when the requesting user is the
    item's creator, preventing unauthorised modifications.
    """
    category = db_session.query(Category).filter_by(name=category_name).first()
    if not category:
        abort(404)
    item = db_session.query(Item).filter_by(
        name=item_name, category_id=category.id
    ).first()
    if not item:
        abort(404)

    # Every item has a non-null user_id, so a simple equality check suffices.
    is_owner = session.get("user_id") == item.user_id
    return render_template(
        "item.html",
        category=category,
        item=item,
        is_owner=is_owner,
    )


# ---------- Create ----------


@catalog_bp.route("/catalog/new", methods=["GET", "POST"])
@login_required
def new_item():
    """Display and process the form to add a new item to the catalog."""
    categories = db_session.query(Category).order_by(Category.name).all()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        category_id = request.form.get("category_id")

        if not name or not category_id:
            flash("Name and category are required.", "danger")
            return render_template("newitem.html", categories=categories)

        new_catalog_item = Item(
            name=name,
            description=description,
            category_id=int(category_id),
            user_id=session["user_id"],
        )
        db_session.add(new_catalog_item)
        db_session.commit()
        flash(f'"{name}" has been added!', "success")
        return redirect(url_for("catalog.show_catalog"))

    return render_template("newitem.html", categories=categories)


# ---------- Update ----------


@catalog_bp.route("/catalog/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
def edit_item(item_id):
    """
    Display and process the edit form for an existing item.

    Returns a flash error and redirects if the logged-in user is not the
    item's creator.
    """
    item = db_session.query(Item).filter_by(id=item_id).first()
    if not item:
        abort(404)

    # Ownership check — only the creator may edit.
    if item.user_id != session["user_id"]:
        flash("You are not authorised to edit this item.", "danger")
        return redirect(
            url_for(
                "catalog.show_item",
                category_name=item.category.name,
                item_name=item.name,
            )
        )

    categories = db_session.query(Category).order_by(Category.name).all()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        category_id = request.form.get("category_id")

        if not name or not category_id:
            flash("Name and category are required.", "danger")
            return render_template("edititem.html", item=item, categories=categories)

        item.name = name
        item.description = description
        item.category_id = int(category_id)
        db_session.commit()
        flash(f'"{name}" has been updated!', "success")
        return redirect(
            url_for(
                "catalog.show_item",
                category_name=item.category.name,
                item_name=item.name,
            )
        )

    return render_template("edititem.html", item=item, categories=categories)


# ---------- Delete ----------


@catalog_bp.route("/catalog/<int:item_id>/delete", methods=["GET", "POST"])
@login_required
def delete_item(item_id):
    """
    Display a confirmation page and process item deletion.

    Returns a flash error and redirects if the logged-in user is not the
    item's creator.
    """
    item = db_session.query(Item).filter_by(id=item_id).first()
    if not item:
        abort(404)

    # Ownership check — only the creator may delete.
    if item.user_id != session["user_id"]:
        flash("You are not authorised to delete this item.", "danger")
        return redirect(
            url_for(
                "catalog.show_item",
                category_name=item.category.name,
                item_name=item.name,
            )
        )

    if request.method == "POST":
        category_name = item.category.name
        item_name = item.name
        db_session.delete(item)
        db_session.commit()
        flash(f'"{item_name}" has been deleted.', "success")
        return redirect(url_for("catalog.show_category", category_name=category_name))

    return render_template("deleteitem.html", item=item)


# ---------- JSON API ----------


@catalog_bp.route("/catalog.json")
def catalog_json():
    """
    Return the entire catalog as JSON.

    Response shape:
        { "categories": [ { "id", "name", "items": [...] }, ... ] }
    """
    categories = db_session.query(Category).order_by(Category.name).all()
    return jsonify(
        categories=[
            {
                "id": category.id,
                "name": category.name,
                "items": [item.serialize for item in category.items],
            }
            for category in categories
        ]
    )


@catalog_bp.route("/catalog/<string:category_name>/items.json")
def category_json(category_name):
    """
    Return all items in a single category as JSON.

    Response shape:
        { "category": "<name>", "items": [...] }
    """
    category = db_session.query(Category).filter_by(name=category_name).first()
    if not category:
        abort(404)
    return jsonify(
        category=category.name,
        items=[item.serialize for item in category.items],
    )
