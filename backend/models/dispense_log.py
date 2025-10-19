from ..import db
from datetime import datetime
from sqlalchemy import func

class DispenseLog(db.Model):
    __tablename__ = 'dispense_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),nullable=False)

    litres_dispensed = db.Column(db.Float, nullable=False)
    tokens_consumed = db.Column(db.Float, nullable=False)

    machine_id =db.Column(db.String(50), nullable = True)
    timestamp=db.Column(db.DateTime, default=func.now(), nullable=False)

    user=db.relationship('User', backref=db.backref('dispense_logs', lazy='dynamic'))

    def __repr__(self):
        return f'<DispenseLog {self.id} | User:{self.user_id} | Litres:{self.litres_dispensed}>'
    
    def to_dict(self):
        return{
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username,
            'litres_dispensed': float(self.litres_dispensed)if self.litres_dispensed is not None else 0.0,
            'tokens_consumed': float(self.tokens_consumed) if self.tokens_consumed is not None else 0.0,
            'machine_id': self.machine_id,
            'timestamp': self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }