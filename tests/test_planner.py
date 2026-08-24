import unittest

from travel_planner.clients import ApiError
from travel_planner.models import Recommendation
from travel_planner.planner import TravelPlanner


class FakeLlm:
    def recommend(self, _date):
        return Recommendation("제주", "온화함", ["봄 축제"], "여행하기 좋은 시기입니다.")

    def write_report(self, _date, _recommendation, _places, _errors):
        return "# 제주 여행 리포트"


class FailingPlaces:
    def search_restaurants(self, _city):
        raise ApiError("HTTP 401")


class PlannerTests(unittest.TestCase):
    def test_place_failure_does_not_stop_report_generation(self):
        recommendation, places, report, errors = TravelPlanner(FakeLlm(), FailingPlaces()).run("2026-10-01")
        self.assertEqual("제주", recommendation.recommended_city)
        self.assertEqual([], places)
        self.assertIn("여행", report)
        self.assertEqual("place_search", errors[0].step)

