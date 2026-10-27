from datetime import timedelta

from config.constants import (
    HIGH_PRIORITY_THRESHOLD, PRIORITY_LABELS, RECENT_ACTIVITY_DAYS,
    STATUS_CANCELLED, STATUS_DONE, STATUS_IN_PROGRESS, STATUS_PENDING,
)
from utils.clock import utc_now
from utils.errors import NotFoundError


def completion_rate(part, total):
    return round((part / total) * 100, 2) if total > 0 else 0


class ReportService:
    def __init__(self, task_repository, user_repository, category_repository):
        self.tasks = task_repository
        self.users = user_repository
        self.categories = category_repository

    def summary(self):
        now = utc_now()
        by_status = self.tasks.count_by_status()
        by_priority = self.tasks.count_by_priority()
        overdue = self.tasks.overdue(now)
        since = now - timedelta(days=RECENT_ACTIVITY_DAYS)

        return {
            'generated_at': str(now),
            'overview': {
                'total_tasks': self.tasks.count(),
                'total_users': self.users.count(),
                'total_categories': self.categories.count(),
            },
            'tasks_by_status': {
                'pending': by_status.get(STATUS_PENDING, 0),
                'in_progress': by_status.get(STATUS_IN_PROGRESS, 0),
                'done': by_status.get(STATUS_DONE, 0),
                'cancelled': by_status.get(STATUS_CANCELLED, 0),
            },
            'tasks_by_priority': {
                label: by_priority.get(priority, 0) for priority, label in PRIORITY_LABELS.items()
            },
            'overdue': {
                'count': len(overdue),
                'tasks': [
                    {
                        'id': task.id,
                        'title': task.title,
                        'due_date': str(task.due_date),
                        'days_overdue': (now - task.due_date).days,
                    }
                    for task in overdue
                ],
            },
            'recent_activity': {
                'tasks_created_last_7_days': self.tasks.count_created_since(since),
                'tasks_completed_last_7_days': self.tasks.count_done_updated_since(since),
            },
            'user_productivity': self._user_productivity(),
        }

    def user_report(self, user_id):
        user = self.users.get(user_id)
        if not user:
            raise NotFoundError('Usuário não encontrado')

        now = utc_now()
        tasks = self.tasks.list_by_user(user_id)
        total = len(tasks)
        count = {status: 0 for status in (STATUS_DONE, STATUS_PENDING, STATUS_IN_PROGRESS, STATUS_CANCELLED)}
        for task in tasks:
            if task.status in count:
                count[task.status] += 1

        return {
            'user': {'id': user.id, 'name': user.name, 'email': user.email},
            'statistics': {
                'total_tasks': total,
                'done': count[STATUS_DONE],
                'pending': count[STATUS_PENDING],
                'in_progress': count[STATUS_IN_PROGRESS],
                'cancelled': count[STATUS_CANCELLED],
                'overdue': sum(1 for task in tasks if task.is_overdue(now)),
                'high_priority': sum(1 for task in tasks if task.priority <= HIGH_PRIORITY_THRESHOLD),
                'completion_rate': completion_rate(count[STATUS_DONE], total),
            },
        }

    def _user_productivity(self):
        totals = self.tasks.count_by_user()
        done = self.tasks.count_done_by_user()
        return [
            {
                'user_id': user.id,
                'user_name': user.name,
                'total_tasks': totals.get(user.id, 0),
                'completed_tasks': done.get(user.id, 0),
                'completion_rate': completion_rate(done.get(user.id, 0), totals.get(user.id, 0)),
            }
            for user in self.users.list_all()
        ]
