from flask import Flask, request, make_response, session
from flask_migrate import Migrate
from marshmallow import ValidationError

from models import db, bcrypt, User, Exercise, Workout, WorkoutExercise
from schemas import ExerciseSchema, WorkoutSchema, WorkoutExerciseSchema

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.secret_key = "secret-key"
bcrypt.init_app(app)

migrate = Migrate(app, db)
db.init_app(app)
exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)

workout_exercise_schema = WorkoutExerciseSchema()

@app.route("/workouts", methods=["GET"])
def get_workouts():
    user_id = session.get("user_id")
    if not user_id:
        return make_response({"error": "Unauthorized"}, 401)
    if not session.get("user_id"):
        return make_response({"error": "Unauthorized"}, 401)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)

    pagination = Workout.query.filter_by(user_id=user_id).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    return make_response({
        "workouts": workouts_schema.dump(pagination.items),
        "page": page,
        "per_page": per_page,
        "total":pagination.total,
        "pages": pagination.pages
    }, 200)

@app.route("/workouts/<int:id>", methods=["GET"])
def get_workout(id):
    user_id = session.get("user_id")
    if not user_id:
        return make_response({"error":"Unauthorized"}, 401)
    
    workout = Workout.query.filter_by(id=id, user_id=user_id).first()

    if not workout:
        return make_response({"error": "Workout not found"}, 404)
    return make_response(workout_schema.dump(workout), 200)

@app.route("/workouts", methods=["POST"])
def create_workout():
    if not session.get("user_id"):
        return make_response({"error": "Unauthorized"}, 401)
    try:
        data = workout_schema.load(request.get_json())

        workout = Workout(
            date=data["date"],
            duration_minutes=data["duration_minutes"],
            notes=data.get("notes"),
            user_id=session["user_id"]

        )

        db.session.add(workout)
        db.session.commit()

        return make_response(workout_schema.dump(workout), 201)
    
    except ValidationError as e:
        return make_response({"errors": e.messages}, 400)
    except ValueError as e:
        return make_response({"error": str(e)}, 400)
@app.route("/workouts/<int:id>", methods=["DELETE"])
def delete_workout(id):
    user_id = session.get("user_id")
    if not user_id:
        return make_response({"error":"Unauthorized"}, 401)
    workout = Workout.query.filter_by(id=id, user_id=user_id).first()

    if not workout:
        return make_response({"error": "Workout not found"}, 404)
   
    db.session.delete(workout)
    db.session.commit()

    return make_response({}, 204)
@app.route("/workouts/<int:id>", methods=["PATCH"])
def update_workout(id):
    user_id = session.get("user_id")

    if not user_id:
        return make_response({"error": "Unauthorized"}, 401)
    
    workout = Workout.query.filter_by(id=id, user_id=user_id).first()

    if not workout:
        return make_response({"error": "Workout not found"}, 404)
    data = request.get_json()
    if "date" in data:
        workout.date = workout_schema.load({"date": data["date"], "duration_minutes": workout.duration_minutes})["date"]
    if "duration_minutes" in data:
        workout.duration_minutes = data["duration_minutes"]
    if "notes" in data:
        workout.notes = data["notes"]
    db.session.commit()

    return make_response(workout_schema.dump(workout), 200)

@app.route("/exercises", methods=["GET"])
def get_exercises():
    exercises = Exercise.query.all()
    return make_response(exercises_schema.dump(exercises), 200)

@app.route("/exercises/<int:id>", methods=["GET"])
def get_exercise(id):
    exercise = Exercise.query.get(id)

    if not exercise:
        return make_response({"error": "Exercise not found"}, 404)
    return make_response(exercise_schema.dump(exercise), 200)

@app.route("/exercises",methods=["POST"])
def create_exercise():
    try:
        data = exercise_schema.load(request.get_json())
        exercise = Exercise(
            name=data["name"],
            category=data["category"],
            equipment_needed=data.get("equipment_needed", False)
        )

        db.session.add(exercise)
        db.session.commit()

        return make_response(exercise_schema.dump(exercise), 201)
    except ValidationError as e:
        return make_response({"errors": e.messages}, 400)

    except ValueError as e:
        return make_response({"error": str(e)}, 400)

@app.route("/exercises/<int:id>", methods=["DELETE"])
def delete_exercise(id):
    exercise = Exercise.query.get(id)

    if not exercise:
        return make_response({"error": "Exercise not found"}, 404)
    
    db.session.delete(exercise)
    db.session.commit()

    return make_response({}, 204)

@app.route("/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises", methods=["POST"])
def add_exercise_to_workout(workout_id, exercise_id):
    user_id = session.get("user_id")
    if not user_id:
        return make_response({"error": "Unauthorized"}, 401)
    workout = Workout.query.filter_by(id=workout_id, user_id=user_id).first()

    exercise = Exercise.query.get(exercise_id)

    if not workout:
        return make_response({"error": "Workout not found"}, 404)
    
    if not exercise:
        return make_response({"error": "Exercise not found"}, 404)
    
    try:
        data = workout_exercise_schema.load(request.get_json())

        workout_exercise = WorkoutExercise(
            workout_id=workout_id,
            exercise_id=exercise_id,
            reps=data.get("reps"),
            sets=data.get("sets"),
            duration_seconds=data.get("duration_seconds")
        )

        db.session.add(workout_exercise)
        db.session.commit()

        return make_response(workout_exercise_schema.dump(workout_exercise), 201)
    except ValidationError as e:
        return make_response({"errors": e.messages}, 400)

    except ValueError as e:
        return make_response({"error": str(e)}, 400)

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    try:
        user = User(username=data.get("username"))
        user.password_hash = data.get("password")

        db.session.add(user)
        db.session.commit()

        session["user_id"] = user.id

        return make_response({
            "id": user.id,
            "username": user.username
        }, 201)

    except Exception as e:
        db.session.rollback()
        return make_response({"errors": [str(e)]}, 422)
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    user = User.query.filter(User.username == data.get("username")).first()

    if user and user.authenticate(data.get("password")):
        session["user_id"] = user.id
        return make_response({
            "id": user.id,
            "username": user.username
        }, 200)
    return make_response({"error": "Invalid username or password"}, 401)
@app.route("/logout", methods=["DELETE"])
def logout():
    session.pop("user_id", None)
    return make_response({}, 204)

@app.route("/check_session", methods=["GET"])
def check_session():
    user_id = session.get("user_id")

    if not user_id:
        return make_response({"error": "Unauthorized"}, 401)
    user = User.query.get(user_id)
    return make_response({
        "id": user.id,
        "username": user.username
    }, 200)
if __name__ == "__main__":
    app.run(port=5555, debug=True)