import json
import subprocess
import sys


def diagnose_pod(pod):
    """Return structured findings for one Kubernetes pod."""
    namespace = pod.get("metadata", {}).get("namespace", "unknown")
    name = pod.get("metadata", {}).get("name", "unknown")
    findings = []

    for status in pod.get("status", {}).get("containerStatuses", []) or []:
        state = status.get("state", {}) or {}
        last_state = status.get("lastState", {}) or {}
        container = status.get("name", "unknown")

        waiting = state.get("waiting")
        if waiting and waiting.get("reason") == "CrashLoopBackOff":
            findings.append({
                "namespace": namespace,
                "name": name,
                "container": container,
                "reason": "CrashLoopBackOff",
            })

        terminated = state.get("terminated")
        if terminated and terminated.get("reason") == "OOMKilled":
            findings.append({
                "namespace": namespace,
                "name": name,
                "container": container,
                "reason": "OOMKilled",
            })

        previous = last_state.get("terminated")
        if previous and previous.get("reason") == "OOMKilled":
            findings.append({
                "namespace": namespace,
                "name": name,
                "container": container,
                "reason": "Previous OOMKilled",
            })

        if status.get("ready") is False and not waiting and not terminated:
            findings.append({
                "namespace": namespace,
                "name": name,
                "container": container,
                "reason": "NotReady",
            })

    return findings


def get_unhealthy_pods():
    print("K8s Pod Doctor health check...")

    try:
        result = subprocess.run(
            ["kubectl", "get", "pods", "--all-namespaces", "-o", "json"],
            capture_output=True,
            text=True,
            check=True,
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
        for finding in diagnose_pod(pod):
            issues_found = True
            prefix = "MEMORY" if "OOMKilled" in finding["reason"] else "ALERT"
            print(
                f"{prefix}: Pod {finding['namespace']}/{finding['name']} "
                f"container {finding['container']} — {finding['reason']}."
            )

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
