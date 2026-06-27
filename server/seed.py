from datetime import date
from app import app
from models import db, User, Exercise, Workout, WorkoutExercise

with app.app_context():
    WorkoutExercise.query.delete()
    Exercise.query.delete()
    Workout.query.delete()
    User.query.delete()

    user= User(username="zanemedua")
    user.password_hash = "1234"

    db.session.add(user)
    db.session.commit()

    benchpress = Exercise(
        name="Bench Press",
        category="Strength",
        equipment_needed=False
    )

    squats = Exercise(
        name="Squats",
        category="Strength",
        equipment_needed=False
    )

    treadmill = Exercise(
        name="Treadmill Run",
        category="Cardio",
        equipment_needed=True
    )

    workout1 = Workout(
        date=date(2026, 6, 20),
        duration_minutes=45,
        notes="Upper body and cardio",
        user_id =user.id
    )

    workout2 = Workout(
        date=date(2026, 6, 21),
        duration_minutes=30,
        notes="Leg day",
        user_id=user.id
    )

    db.session.add_all([benchpress, squats, treadmill, workout1, workout2])
    db.session.commit()

    we1 = WorkoutExercise(
        workout_id=workout1.id,
        exercise_id=benchpress.id,
        reps=8,
        sets=3
    )

    we2 = WorkoutExercise(
        workout_id=workout1.id,
        exercise_id=treadmill.id,
        duration_seconds=900
    )

    we3 = WorkoutExercise(
        workout_id=workout2.id,
        exercise_id=squats.id,
        reps=12,
        sets=4
    )

    db.session.add_all([we1, we2, we3])
    db.session.commit()


    print("Database seeded")