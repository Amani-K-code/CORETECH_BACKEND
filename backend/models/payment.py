from .. import db
from datetime import datetime
from sqlalchemy  import func

class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    #Transaction and token details
    amount = db.Column(db.Float, nullable=False)
    tokens_purchased = db.Column(db.Integer, nullable=False)

    #transaction details for real MPESA integration in the future
    transaction_id = db.Column(db.String(100), unique=True, nullable = True)
    status = db.Column(db.String(50), nullable=False, default = 'completed')

    #Timestamps
    created_at= db.Column(db.DateTime, default=func.now(), nullable=False)

    #Relationships
    user = db.relationship('User', backref=db.backref('payments', lazy='dynamic'))

    def __repr__(self):
        return f'<Payment {self.id} | User:{self.user_id} | Amount{self.amount} | Status:{self.status}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'tokens_purchased': self.tokens_purchased,
            'transaction_id': self.transaction_id,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
