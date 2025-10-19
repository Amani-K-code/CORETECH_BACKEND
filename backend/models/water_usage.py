from datetime import datetime
from ..import db



class WaterUsage(db.Model):
    id = db.Column(db.Integer, primary_key =True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    litres_dispensed = db.Column(db.Float, nullable=False)
    tokens_used = db.Column(db.Float, nullable = False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    #Optional relationship for user to link back to user object
    user= db.relationship('User', backref=db.backref('usage_history', lazy=True))

    def to_dict(self):
        return{
            'id': self.id,
            'user_id':self.user_id,
            'litres_dispensed': self.litres_dispensed,
            'tokens_used': self.tokens_used,
            'timestamp': self.timestamp.isoformat()
        }