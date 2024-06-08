from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def setup_db(app, database_path="sqlite:///./database.db"):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.drop_all()
    db.create_all()

class Drink(db.Model):
    __tablename__ = 'drinks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)

    recipes = db.relationship("Recipe", back_populates="drink",
                            lazy="joined", uselist=True, cascade="all,delete")

    def short(self):
        return {
            'id': self.id,
            'name': self.title
        }

    def long(self):
        return {
            'id': self.id,
            'name': self.title,
            'recipe': [recipe.short() for recipe in self.recipes]
        }

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Recipe(db.Model):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    ingredient_name = db.Column(db.String, nullable=False)
    number_of_parts = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String, nullable=False)
    drink_id = db.Column(db.Integer, db.ForeignKey(Drink.id))

    drink = db.relationship(
        "Drink", back_populates="recipes")

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def short(self):
        return {
            "name": self.ingredient_name,
            "parts": self.number_of_parts,
            "color": self.color
        }