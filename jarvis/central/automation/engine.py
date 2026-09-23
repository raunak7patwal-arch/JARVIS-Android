import threading
import time


class AutomationEngine:

    ALLOWED_ACTIONS = {
        "smart_home",
        "device_command",
        "notification",
        "memory",
    }

    def __init__(self):
        self.jobs = {}
        self.lock = threading.RLock()

    def add(
        self,
        job_id,
        name,
        action,
        parameters=None,
        enabled=True
    ):
        action = str(
            action
        ).strip().lower()

        if action not in self.ALLOWED_ACTIONS:
            return False

        if not job_id or not name:
            return False

        with self.lock:
            self.jobs[job_id] = {
                "id": job_id,
                "name": name,
                "action": action,
                "parameters": (
                    parameters
                    if isinstance(
                        parameters,
                        dict
                    )
                    else {}
                ),
                "enabled": bool(enabled),
                "created": time.time(),
                "last_run": None,
            }

        return True

    def enable(self, job_id):
        with self.lock:
            if job_id not in self.jobs:
                return False

            self.jobs[job_id]["enabled"] = True
            return True

    def disable(self, job_id):
        with self.lock:
            if job_id not in self.jobs:
                return False

            self.jobs[job_id]["enabled"] = False
            return True

    def remove(self, job_id):
        with self.lock:
            return (
                self.jobs.pop(
                    job_id,
                    None
                )
                is not None
            )

    def get(self, job_id):
        with self.lock:
            job = self.jobs.get(job_id)

            return (
                dict(job)
                if job
                else None
            )

    def list_jobs(self):
        with self.lock:
            return [
                dict(job)
                for job in self.jobs.values()
            ]

    def mark_run(self, job_id):
        with self.lock:
            if job_id not in self.jobs:
                return False

            self.jobs[job_id]["last_run"] = (
                time.time()
            )

            return True


automation = AutomationEngine()
