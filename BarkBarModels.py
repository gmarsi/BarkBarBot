import datetime

from peewee import *

# Initialize db
db = SqliteDatabase('BarkBar.db')

# Define models
class Menu(Model):
    name = CharField()
    description = TextField(null=True)
    active = BooleanField(default=False)

    class Meta:
        database = db

class MenuSection(Model):
    name = CharField()
    description = TextField(null=True)
    menu = ForeignKeyField(Menu, backref='menu_sections')
    active = BooleanField(default=True)
    
    class Meta:
        database = db

class MenuItem(Model):
    name = CharField()
    description = TextField(null=True)
    menu = ForeignKeyField(Menu, backref='menu_items')
    menu_section = ForeignKeyField(MenuSection, backref='section_items')
    active = BooleanField(default=True)

    class Meta:
        database = db

class Order(Model):
    item = ForeignKeyField(MenuItem, backref='orders')
    customer_name = CharField()
    instructions = TextField(null=True)
    created_date = DateTimeField(default=datetime.datetime.now)
    fulfilled_date = DateTimeField(null=True)
    order_status = CharField() # use "pending", "completed", or "canceled" 

    class Meta:
        database = db

class Staff(Model):
    telegram_handle = CharField()
    active = BooleanField(default=True)
    is_admin = BooleanField(default=False)

    class Meta:
        database = db


# Uncomment to build db from scratch
db.create_tables([Menu, MenuSection, MenuItem, Order, Staff])