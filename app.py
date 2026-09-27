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


class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    borrowed_on = db.Column(db.Date, nullable=False)
    due_on = db.Column(db.Date, nullable=False)

    member_id = db.Column(db.Integer, db.ForeignKey("member.id"), nullable=False)
    duck_id = db.Column(db.Integer, db.ForeignKey("duck.id"), nullable=False)

    member = db.relationship("Member", backref=db.backref("loans", lazy=True))
    duck = db.relationship("Duck", backref=db.backref("loans", lazy=True))


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
        Duck(name="Debuggy"),
        Duck(name="Quacky"),
        Duck(name="Rubber"),
        Duck(name="Sir Ducksworth"),
        Duck(name="Yellow"),
    ]
    db.session.add_all(ducks)
    db.session.commit()

    today = date.today()

    # These loans are due exactly 3 days from today and should appear.
    loans = [
        Loan(member_id=members[0].id, duck_id=ducks[0].id,
             borrowed_on=today - timedelta(days=4), due_on=today + timedelta(days=3)),
        Loan(member_id=members[0].id, duck_id=ducks[0].id,
             borrowed_on=today - timedelta(days=2), due_on=today + timedelta(days=3)),
        Loan(member_id=members[0].id, duck_id=ducks[1].id,
             borrowed_on=today - timedelta(days=3), due_on=today + timedelta(days=3)),
        Loan(member_id=members[1].id, duck_id=ducks[2].id,
             borrowed_on=today - timedelta(days=1), due_on=today + timedelta(days=3)),
        Loan(member_id=members[1].id, duck_id=ducks[3].id,
             borrowed_on=today - timedelta(days=5), due_on=today + timedelta(days=3)),
        Loan(member_id=members[2].id, duck_id=ducks[4].id,
             borrowed_on=today - timedelta(days=2), due_on=today + timedelta(days=3)),

        # Not due in 3 days, demonstrating that it is filtered out.
        Loan(member_id=members[3].id, duck_id=ducks[0].id,
             borrowed_on=today, due_on=today + timedelta(days=7)),
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

    # Group loans by member, then group the same duck together.
    grouped = []
    for member in sorted({loan.member for loan in loans}, key=lambda m: m.name):
        member_loans = [loan for loan in loans if loan.member_id == member.id]

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
