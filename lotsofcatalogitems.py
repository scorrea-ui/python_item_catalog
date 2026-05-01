"""
Seed script — populates the database with a system user, categories, and items.

Run this script after starting the database and creating the tables:
    python models.py
    python lotsofcatalogitems.py

The script is idempotent: running it multiple times clears and re-seeds
item and category data without duplicating the system user.
"""

from database import db_session, engine
from models import Base, Category, Item, User

# The system user owns all seeded items. Using a non-routable email
# domain ensures no real Google account can match this address.
SYSTEM_USER_NAME = "Catalog Admin"
SYSTEM_USER_EMAIL = "system@catalog.local"

Base.metadata.create_all(engine)


def get_or_create_system_user():
    """Return the system user, creating it if it does not already exist."""
    system_user = db_session.query(User).filter_by(email=SYSTEM_USER_EMAIL).first()
    if not system_user:
        system_user = User(
            name=SYSTEM_USER_NAME,
            email=SYSTEM_USER_EMAIL,
            picture="",
        )
        db_session.add(system_user)
        db_session.commit()
        print(f"System user created (id={system_user.id}).")
    else:
        print(f"System user already exists (id={system_user.id}).")
    return system_user


def seed_categories_and_items(system_user):
    """Delete existing seed data and insert fresh categories and items."""
    # Delete items before categories to respect the foreign-key constraint.
    db_session.query(Item).delete()
    db_session.query(Category).delete()
    db_session.commit()

    # ---- Categories ----
    soccer = Category(name="Soccer")
    basketball = Category(name="Basketball")
    baseball = Category(name="Baseball")
    frisbee = Category(name="Frisbee")
    snowboarding = Category(name="Snowboarding")
    rock_climbing = Category(name="Rock Climbing")
    foosball = Category(name="Foosball")
    skating = Category(name="Skating")
    hockey = Category(name="Hockey")

    db_session.add_all([
        soccer, basketball, baseball, frisbee,
        snowboarding, rock_climbing, foosball, skating, hockey,
    ])
    db_session.commit()

    # ---- Items ----
    # All seeded items are owned by the system user so that regular users
    # cannot accidentally edit or delete the default catalog content.
    db_session.add_all([
        Item(
            name="Stick",
            description=(
                "A hockey stick is a piece of equipment used in field hockey "
                "or ice hockey to move the puck or ball."
            ),
            category=hockey,
            user_id=system_user.id,
        ),
        Item(
            name="Goggles",
            description=(
                "Snowboarding goggles protect your eyes from UV rays, wind, "
                "and debris while keeping your vision clear on the slopes."
            ),
            category=snowboarding,
            user_id=system_user.id,
        ),
        Item(
            name="Snowboard",
            description=(
                "Best for any terrain and conditions. All-mountain snowboards "
                "perform anywhere on a mountain — groomed runs, backcountry, "
                "even park and pipe. They may be directional (downhill only) "
                "or twin-tip (for riding switch). Most boarders ride all-mountain "
                "boards because of their versatility, making them ideal for "
                "beginners still learning what terrain they prefer."
            ),
            category=snowboarding,
            user_id=system_user.id,
        ),
        Item(
            name="Two Shinguards",
            description=(
                "Shinguards protect the lower leg from impact during play. "
                "Essential protective gear for soccer players at every level."
            ),
            category=soccer,
            user_id=system_user.id,
        ),
        Item(
            name="Shinguards",
            description=(
                "Protective gear worn on the shins to guard against kicks "
                "and collisions on the pitch."
            ),
            category=soccer,
            user_id=system_user.id,
        ),
        Item(
            name="Frisbee",
            description=(
                "A frisbee (also called a flying disc) is a gliding toy or "
                "sporting item that is generally plastic and roughly 20-25 cm "
                "in diameter."
            ),
            category=frisbee,
            user_id=system_user.id,
        ),
        Item(
            name="Bat",
            description=(
                "A baseball bat is a smooth wooden or metal club used in the "
                "sport of baseball to hit the ball after it is thrown by the "
                "pitcher."
            ),
            category=baseball,
            user_id=system_user.id,
        ),
        Item(
            name="Jersey",
            description=(
                "A breathable, lightweight jersey for soccer. "
                "Available in team colours."
            ),
            category=soccer,
            user_id=system_user.id,
        ),
        Item(
            name="Soccer Cleats",
            description=(
                "Soccer cleats provide traction on grass surfaces and protect "
                "the feet during matches."
            ),
            category=soccer,
            user_id=system_user.id,
        ),
        Item(
            name="Basketball",
            description=(
                "A standard NBA-size basketball, suitable for indoor and "
                "outdoor courts."
            ),
            category=basketball,
            user_id=system_user.id,
        ),
        Item(
            name="Climbing Harness",
            description=(
                "A sit harness that provides comfort and security for "
                "sport and trad rock climbing."
            ),
            category=rock_climbing,
            user_id=system_user.id,
        ),
        Item(
            name="Inline Skates",
            description=(
                "High-performance inline skates suitable for recreational "
                "and aggressive skating."
            ),
            category=skating,
            user_id=system_user.id,
        ),
    ])
    db_session.commit()


if __name__ == "__main__":
    active_system_user = get_or_create_system_user()
    seed_categories_and_items(active_system_user)
    print("Database seeded successfully.")
