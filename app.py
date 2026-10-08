from flask import Flask, render_template, request
from datetime import date

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/calculate", methods=["POST"])
def calculate():

    # Semester information
    start_date = date.fromisoformat(
        request.form["start_date"]
    )

    end_date = date.fromisoformat(
        request.form["end_date"]
    )

    threshold = float(
        request.form["threshold"]
    )

    number_of_subjects = int(
        request.form["number_of_subjects"]
    )

    # Calculate semester progress
    today = date.today()

    if today < start_date:
        elapsed_days = 0

    elif today > end_date:
        elapsed_days = (
            end_date - start_date
        ).days

    else:
        elapsed_days = (
            today - start_date
        ).days

    remaining_days = max(
        0,
        (end_date - max(today, start_date)).days
    )

    elapsed_weeks = elapsed_days / 7
    remaining_weeks = remaining_days / 7

    subjects = []

    total_conducted = 0
    total_attended = 0
    total_remaining = 0

    # Read subjects
    for i in range(number_of_subjects):

        name = request.form[
            f"name_{i}"
        ]

        classes_per_week = float(
            request.form[
                f"classes_{i}"
            ]
        )

        attendance = float(
            request.form[
                f"attendance_{i}"
            ]
        )

        conducted = (
            elapsed_weeks *
            classes_per_week
        )

        remaining = (
            remaining_weeks *
            classes_per_week
        )

        attended = (
            conducted *
            attendance / 100
        )

        # Calculate safe skips
        if conducted <= 0:
            safe_skips = 0

        elif attendance < threshold:
            safe_skips = 0

        else:
            maximum_skips = (
                attended / (threshold / 100)
            ) - conducted

            safe_skips = min(
                maximum_skips,
                remaining
            )

            safe_skips = max(
                0,
                int(safe_skips)
            )

        subjects.append({
            "name": name,
            "classes_per_week": classes_per_week,
            "attendance": attendance,
            "conducted": conducted,
            "remaining": remaining,
            "safe_skips": safe_skips
        })

        total_conducted += conducted
        total_attended += attended
        total_remaining += remaining

    # Overall attendance
    if total_conducted > 0:
        overall_attendance = (
            total_attended /
            total_conducted
        ) * 100
    else:
        overall_attendance = 0

    total_safe_skips = sum(
        subject["safe_skips"]
        for subject in subjects
    )

    return render_template(
        "results.html",
        subjects=subjects,
        threshold=threshold,
        overall_attendance=overall_attendance,
        total_remaining=total_remaining,
        total_safe_skips=total_safe_skips
    )


if __name__ == "__main__":
    app.run(debug=True)