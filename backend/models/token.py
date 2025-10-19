from .. import db


class Token(db.Model):
    __tablename__= 'tokens'

    id= db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable= False)
    balance= db.Column(db.Integer, default=0, nullable=False)

    def __repr__(self):
        return f'<Token for user_id{self.user_id}'