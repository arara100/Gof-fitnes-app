from app.patterns.report_generator import (
    AverageActivityReport, PopularWorkoutsReport, ProgressReport, ReportParams,
)
from app.services.errors import ServiceError


class ReportService:
    """Runs a named report; each report is a ReportGenerator (Template Method)."""

    def __init__(self, generators=None):
        self.generators = generators or {
            "progress": ProgressReport(),
            "popular": PopularWorkoutsReport(),
            "activity": AverageActivityReport(),
        }

    def run(self, name, user_id=None, date_from=None, date_to=None, limit=10):
        generator = self.generators.get(name)
        if generator is None:
            raise ServiceError(f"Unknown report: {name}", 404)
        if date_from and date_to and date_to < date_from:
            raise ServiceError("'to' must not be before 'from'", 422)
        return generator.generate(
            ReportParams(int(user_id) if user_id else None, date_from, date_to, limit)
        )
