import unittest

from doctor import diagnose_pod


class PodDoctorTests(unittest.TestCase):
    def test_crash_loop(self):
        pod = {
            "metadata": {"namespace": "production", "name": "api-1"},
            "status": {"containerStatuses": [{
                "name": "api",
                "state": {"waiting": {"reason": "CrashLoopBackOff"}},
            }]},
        }
        findings = diagnose_pod(pod)
        self.assertEqual(findings[0]["reason"], "CrashLoopBackOff")

    def test_oom_killed(self):
        pod = {
            "metadata": {"namespace": "production", "name": "api-2"},
            "status": {"containerStatuses": [{
                "name": "api",
                "state": {"terminated": {"reason": "OOMKilled"}},
            }]},
        }
        findings = diagnose_pod(pod)
        self.assertEqual(findings[0]["reason"], "OOMKilled")

    def test_previous_oom_killed(self):
        pod = {
            "metadata": {"namespace": "production", "name": "api-3"},
            "status": {"containerStatuses": [{
                "name": "api",
                "state": {},
                "lastState": {"terminated": {"reason": "OOMKilled"}},
            }]},
        }
        findings = diagnose_pod(pod)
        self.assertEqual(findings[0]["reason"], "Previous OOMKilled")

    def test_healthy(self):
        pod = {
            "metadata": {"namespace": "production", "name": "api-4"},
            "status": {"containerStatuses": [{
                "name": "api",
                "ready": True,
                "state": {"running": {}},
            }]},
        }
        self.assertEqual(diagnose_pod(pod), [])


if __name__ == "__main__":
    unittest.main()
