from datetime import date
import unittest

from app import app, db, Member, DeluxeDuck, Loan


class TestDeluxeDuck(unittest.TestCase):

    def test_deluxe_duck_has_14_day_due_date(self):
        with app.app_context():
            db.drop_all()
            db.create_all()

            member = Member(name="Test Member")
            duck = DeluxeDuck(name="Deluxe Duck")

            db.session.add_all([member, duck])
            db.session.commit()

            borrowed_on = date(2026, 9, 27)

            loan = Loan(
                member=member,
                duck=duck,
                borrowed_on=borrowed_on,
                due_on=borrowed_on
            )

            self.assertEqual(
                loan.calculate_due_date(),
                date(2026, 10, 11)
            )


if __name__ == "__main__":
    unittest.main()