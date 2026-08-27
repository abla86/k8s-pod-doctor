# K8s Pod Doctor

A small Day-2 operations CLI for quickly identifying common Kubernetes workload failure states across namespaces.

## Detects

- CrashLoopBackOff
- OOMKilled
- Previous OOMKilled termination
- Containers that are not ready
- Other container waiting reasons

## Usage

```powershell
python doctor.py
```

## Requirements

- Python 3.10+
- kubectl
- Access to the target Kubernetes cluster

## Day-2 workflow

```text
Kubernetes workload
        |
        v
    Pod Doctor
        |
        +--> CrashLoopBackOff
        +--> OOMKilled
        +--> NotReady
        +--> Waiting reason
        |
        v
kubectl describe / logs / events / metrics
```

The tool performs first-line status diagnosis. It does not automatically mutate or restart workloads.

## Exit codes

`0` means no configured failure condition was detected.

`1` means a failure condition was detected or Kubernetes could not be inspected.

## License

MIT
