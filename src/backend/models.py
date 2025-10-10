from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey, DECIMAL, TIMESTAMP, func, ARRAY
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography, Geometry
from datetime import datetime
from .db import Base

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    xp_points = Column(Integer, default=0)

class Place(Base):
    __tablename__ = "places"
    place_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    place_types = Column(ARRAY(String))
    google_place_id = Column(String)
    bounding_box = Column(Geometry("POLYGON", srid=4326))

class LocationHistory(Base):
    __tablename__ = "location_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    location = Column(Geography("POINT", srid=4326))
    timestamp = Column(DateTime, default=datetime.utcnow)
    user = relationship("User")

class Enemy(Base):
    __tablename__ = "enemies"

    id = Column(Integer, primary_key=True, index=True)
    enemy_type = Column(String, nullable=False)   # e.g. "Troll", "Sphinx"
    location = Column(Geometry("POINT", srid=4326), nullable=False)
    riddle = Column(String)
    answer = Column(String)
    spawn_time = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    defeated = Column(Integer, default=0)  # 0 = active, 1 = solved
    user_id = Column(Integer, ForeignKey("users.user_id"))  # player-specific

#### An older, more comprehensive version

# # =====================
# # Classes (character archetypes)
# # =====================
# class Class(Base):
#     __tablename__ = "classes"
#
#     class_id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(50), unique=True, nullable=False)
#     description = Column(Text)
#
#     users = relationship("User", back_populates="class_")
#
# # =====================
# # Users
# # =====================
# class User(Base):
#     __tablename__ = "users"
#
#     user_id = Column(Integer, primary_key=True, index=True)
#     username = Column(String(50), unique=True, nullable=False)
#     email = Column(String(100), unique=True, nullable=False)
#     password_hash = Column(Text, nullable=False)
#     created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
#
#     class_id = Column(Integer, ForeignKey("classes.class_id"))
#     class_ = relationship("Class", back_populates="users")
#
#     stats = relationship("PlayerStats", back_populates="user", uselist=False)
#     inventory = relationship("Inventory", back_populates="user")
#     loot_logs = relationship("LootLog", back_populates="user")
#
# # =====================
# # Player Stats
# # =====================
# class PlayerStats(Base):
#     __tablename__ = "player_stats"
#
#     user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
#     level = Column(Integer, default=1)
#     experience = Column(Integer, default=0)
#     health = Column(Integer, default=100)
#     mana = Column(Integer, default=50)
#     strength = Column(Integer, default=5)
#     agility = Column(Integer, default=5)
#     intelligence = Column(Integer, default=5)
#
#     user = relationship("User", back_populates="stats")
#
# # =====================
# # Items (loot definitions)
# # =====================
# class Item(Base):
#     __tablename__ = "items"
#
#     item_id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(100), nullable=False)
#     description = Column(Text)
#     item_type = Column(String(50))  # weapon, armor, consumable, etc.
#     rarity = Column(String(20), default="common")
#
#     inventories = relationship("Inventory", back_populates="item")
#     loot_logs = relationship("LootLog", back_populates="item")
#
# # =====================
# # Inventory
# # =====================
# class Inventory(Base):
#     __tablename__ = "inventory"
#
#     inventory_id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.user_id"))
#     item_id = Column(Integer, ForeignKey("items.item_id"))
#     quantity = Column(Integer, default=1)
#
#     user = relationship("User", back_populates="inventory")
#     item = relationship("Item", back_populates="inventories")
#
# # =====================
# # Locations
# # =====================
# class Location(Base):
#     __tablename__ = "locations"
#
#     location_id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(100), nullable=False)
#     latitude = Column(DECIMAL(9, 6), nullable=False)
#     longitude = Column(DECIMAL(9, 6), nullable=False)
#     place_type = Column(String(50))
#
#     loot_logs = relationship("LootLog", back_populates="location")
#
# # =====================
# # Loot Log
# # =====================
# class LootLog(Base):
#     __tablename__ = "loot_log"
#
#     log_id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.user_id"))
#     item_id = Column(Integer, ForeignKey("items.item_id"))
#     location_id = Column(Integer, ForeignKey("locations.location_id"))
#     found_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
#
#     user = relationship("User", back_populates="loot_logs")
#     item = relationship("Item", back_populates="loot_logs")
#     location = relationship("Location", back_populates="loot_logs")
