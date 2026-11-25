import unittest

from app.fucn.planner_helpers import build_day_plan


class DayPlanTests(unittest.TestCase):
    def test_only_open_tasks_receive_time_slots(self):
        tasks = [
            {'title': 'Закрытая', 'status': 'done', 'priority': 'high'},
            {'title': 'Открытая', 'status': 'pending', 'duration_minutes': 30},
        ]
        self.assertEqual(build_day_plan(tasks, {}, '2026-11-25'), '• 09:00-09:30 — Открытая')

    def test_all_done_is_distinct_from_an_empty_day(self):
        done = [{'title': 'Закрытая', 'status': 'done'}]
        self.assertIn('выполнены', build_day_plan(done, {}, '2026-11-25'))
        self.assertIn('задач нет', build_day_plan([], {}, '2026-11-25'))
