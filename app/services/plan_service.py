from app.patterns.plan_builder import PlanBuilder
from app.patterns.plan_decorator import BasePlan, StretchDecorator, WarmUpDecorator
from app.patterns.plan_strategy import get_strategy
from app.repositories.plan_repository import PlanRepository
from app.repositories.user_repository import UserRepository
from app.repositories.workout_repository import WorkoutRepository
from app.services.errors import ServiceError


class PlanService:
    """Creates and reads personal programs.

    Uses: PlanStrategy (pick workouts for a goal), PlanBuilder (assemble the plan),
    decorators (optional warm-up / stretching in the rendered view).
    """

    def __init__(self, plans=None, workouts=None, users=None):
        self.plans = plans or PlanRepository()
        self.workouts = workouts or WorkoutRepository()
        self.users = users or UserRepository()

    def _user(self, user_id):
        user = self.users.get(int(user_id))
        if not user:
            raise ServiceError("User not found", 404)
        return user

    def list(self, user_id):
        return self.plans.list_for_user(int(user_id))

    def get(self, user_id, plan_id):
        plan = self.plans.get_for_user(plan_id, int(user_id))
        if not plan:
            raise ServiceError("Plan not found", 404)
        return plan

    def generate(self, user_id, goal=None, name=None):
        """Build a plan automatically: the goal comes from the request or the user's profile."""
        user = self._user(user_id)
        goal = goal or (user.profile.goal if user.profile else None)
        if not goal:
            raise ServiceError("Goal is required: pass it or set it in the profile", 422)
        # Strategy: the goal selects the schedule rules; the service never branches on goal itself.
        strategy = get_strategy(goal)
        by_type = {}
        for workout in self.workouts.search():
            by_type.setdefault(workout.type, []).append(workout)
        builder = PlanBuilder().for_user(user).named(name or f"План: {goal}").goal(goal)
        for day, workout in strategy.select(by_type):
            builder.add_workout(workout, day)
        return self._save(builder.build())

    def create_custom(self, user_id, name, items, goal=None):
        builder = PlanBuilder().for_user(self._user(user_id)).named(name).goal(goal)
        for item in items:
            workout = self.workouts.get(item["workout_id"])
            if not workout:
                raise ServiceError(f"Workout {item['workout_id']} not found", 404)
            builder.add_workout(workout, item["day_of_week"])
        return self._save(builder.build())

    def delete(self, user_id, plan_id):
        self.plans.delete(self.get(user_id, plan_id))
        self.plans.commit()

    @staticmethod
    def render(plan, warmup=False, stretch=False):
        """Return plan entries, optionally wrapped in decorators."""
        component = BasePlan(plan)
        if warmup:
            component = WarmUpDecorator(component)
        if stretch:
            component = StretchDecorator(component)
        return component.entries()

    def _save(self, plan):
        self.plans.add(plan)
        self.plans.commit()
        return plan
