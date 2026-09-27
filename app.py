from datetime import date, timedelta

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


class Duck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # Used by SQLAlchemy to map rows to the correct subclass.
    duck_type = db.Column(db.String(20), nullable=False)

    __mapper_args__ = {
        "polymorphic_on": duck_type,
        "polymorphic_identity": "duck"
    }

    def get_loan_period(self):
        raise NotImplementedError


class StandardDuck(Duck):
    __mapper_args__ = {
        "polymorphic_identity": "standard"
    }

    loan_period = 7
    deposit = 0.0

    def get_loan_period(self):
        return self.loan_period


class DeluxeDuck(Duck):
    __mapper_args__ = {
        "polymorphic_identity": "deluxe"
    }

    loan_period = 14
    deposit = 10.0

    def get_loan_period(self):
        return self.loan_period


class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    borrowed_on = db.Column(db.Date, nullable=False)
    due_on = db.Column(db.Date, nullable=False)

    member_id = db.Column(
        db.Integer,
        db.ForeignKey("member.id"),
        nullable=False
    )

    duck_id = db.Column(
        db.Integer,
        db.ForeignKey("duck.id"),
        nullable=False
    )

    member = db.relationship(
        "Member",
        backref=db.backref("loans", lazy=True)
    )

    duck = db.relationship(
        "Duck",
        backref=db.backref("loans", lazy=True)
    )

    def calculate_due_date(self):
        return self.borrowed_on + timedelta(
            days=self.duck.get_loan_period()
        )


def seed_database():
    db.create_all()

    members = [
        Member(name="Alice Tan"),
        Member(name="Ben Lim"),
        Member(name="Chloe Wong"),
        Member(name="Daniel Lee"),
    ]
    db.session.add_all(members)

    ducks = [
        StandardDuck(name="Debuggy"),
        StandardDuck(name="Quacky"),
        StandardDuck(name="Rubber"),
        StandardDuck(name="Sir Ducksworth"),
        DeluxeDuck(name="Deluxe Duck"),
    ]
    db.session.add_all(ducks)
    db.session.commit()

    today = date.today()

    loans = [
        Loan(
            member_id=members[0].id,
            duck_id=ducks[0].id,
            borrowed_on=today - timedelta(days=4),
            due_on=today + timedelta(days=3)
        ),
        Loan(
            member_id=members[0].id,
            duck_id=ducks[0].id,
            borrowed_on=today - timedelta(days=2),
            due_on=today + timedelta(days=3)
        ),
        Loan(
            member_id=members[0].id,
            duck_id=ducks[1].id,
            borrowed_on=today - timedelta(days=3),
            due_on=today + timedelta(days=3)
        ),
        Loan(
            member_id=members[1].id,
            duck_id=ducks[2].id,
            borrowed_on=today - timedelta(days=1),
            due_on=today + timedelta(days=3)
        ),
        Loan(
            member_id=members[1].id,
            duck_id=ducks[3].id,
            borrowed_on=today - timedelta(days=5),
            due_on=today + timedelta(days=3)
        ),
        Loan(
            member_id=members[2].id,
            duck_id=ducks[4].id,
            borrowed_on=today - timedelta(days=2),
            due_on=today + timedelta(days=3)
        ),
    ]

    db.session.add_all(loans)
    db.session.commit()


@app.route("/")
def reminders():
    target_date = date.today() + timedelta(days=3)

    loans = (
        Loan.query
        .filter(Loan.due_on == target_date)
        .order_by(Loan.member_id, Loan.duck_id)
        .all()
    )

    grouped = []

    for member in sorted(
        {loan.member for loan in loans},
        key=lambda member: member.name
    ):
        member_loans = [
            loan for loan in loans
            if loan.member_id == member.id
        ]

        duck_groups = {}

        for loan in member_loans:
            duck_groups.setdefault(loan.duck.name, 0)
            duck_groups[loan.duck.name] += 1

        grouped.append({
            "member": member,
            "duck_groups": sorted(duck_groups.items()),
            "total_ducks": len(member_loans),
        })

    return render_template(
        "reminders.html",
        grouped=grouped,
        target_date=target_date,
        total_ducks=len(loans),
    )


with app.app_context():
    seed_database()


if __name__ == "__main__":
    app.run(debug=True)