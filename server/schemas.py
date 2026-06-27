from marshmallow import Schema, fields, validate, validates_schema, ValidationError

class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=2))
    category = fields.Str(required=True, validate=validate.Length(min=2))
    equipment_needed = fields.Bool()

    workout_exercises = fields.List(
        fields.Nested(lambda: WorkoutExerciseSchema(exclude=("exercise",)))
    )

class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True, validate=validate.Range(min=1))
    notes = fields.Str(allow_none=True)

    workout_exercises = fields.List(
        fields.Nested(lambda: WorkoutExerciseSchema(exclude=("workout",)))
    )

class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)

    reps = fields.Int(allow_none=True, validate=validate.Range(min=0))
    sets = fields.Int(allow_none=True, validate=validate.Range(min=0))
    duration_seconds = fields.Int(allow_none=True, validate=validate.Range(min=0))

    workout = fields.Nested(lambda: WorkoutSchema(exclude=("workout_exercises",)))
    exercise = fields.Nested(lambda: ExerciseSchema(exclude=("workout_exercises",)))

    @validates_schema
    def validate_tracking_data(self, data, **kwargs):
        if not data.get("duration_seconds") and not data.get("reps"):
            raise ValidationError("Must include either reps or duration_seconds.")