from .. import db
from datetime import datetime

class Water(db.Model):
    __tablename__ = 'water'
    id = db.Column(db.Integer, primary_key=True)
    capacity_litres = db.Column(db.Numeric(15,2), nullable=False)
    current_litres = db.Column(db.Numeric(15,2), nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow,nullable=False)

    def __repr__(self):
        return f'<Water {self.id}>'
