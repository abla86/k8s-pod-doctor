import json
import subprocess
import sys

def get_unhealthy_pods():
    print("K8s Pod Doctor health check...")

    try:
        result = subprocess.run(
            [
                "kubectl",
                "get",
                "pods",
                "--all-namespaces",
                "-o",
                "json"
            ],
            capture_output=True,
            text=True,
            check=True
        )

        data = json.loads(result.stdout)

    except FileNotFoundError:
        print("ERROR: kubectl is not installed or not in PATH.")
        return 1

    except subprocess.CalledProcessError as exc:
        print("ERROR: Could not query Kubernetes.")
        print(exc.stderr.strip())
        return 1

    except json.JSONDecodeError:
        print("ERROR: kubectl returned invalid JSON.")
        return 1

    issues_found = False

    for pod in data.get("items", []):
        namespace = pod.get("metadata", {}).get("namespace", "unknown")
        name = pod.get("metadata", {}).get("name", "unknown")

        statuses = (
            pod.get("status", {})
            .get("containerStatuses", [])
            or []
        )

        for status in statuses:
            state = status.get("state", {}) or {}
            last_state = status.get("lastState", {}) or {}

            waiting = state.get("waiting")

            if waiting and waiting.get("reason") == "CrashLoopBackOff":
                print(
                    f"ALERT: Pod {namespace}/{name} "
                    f"is in CrashLoopBackOff."
                )
                issues_found = True

            terminated = state.get("terminated")

            if terminated and terminated.get("reason") == "OOMKilled":
                print(
                    f"MEMORY: Pod {namespace}/{name} "
                    f"was OOMKilled."
                )
                issues_found = True

            previous = last_state.get("terminated")

            if previous and previous.get("reason") == "OOMKilled":
                print(
                    f"MEMORY: Pod {namespace}/{name} "
                    f"was previously OOMKilled."
                )
                issues_found = True

            if (
                status.get("ready") is False
                and not waiting
                and not terminated
            ):
                print(
                    f"NOT READY: Pod {namespace}/{name} "
                    f"container {status.get('name', 'unknown')}."
                )
                issues_found = True

    if not issues_found:
        print("No configured unhealthy pod conditions detected.")
        return 0

    print(
        "\nRecommendation: inspect the affected pod with "
        "'kubectl describe pod' and 'kubectl logs'."
    )

    return 1


if __name__ == "__main__":
    sys.exit(get_unhealthy_pods())
