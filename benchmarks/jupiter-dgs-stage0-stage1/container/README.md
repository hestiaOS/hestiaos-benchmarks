# Container path (optional, secondary)

The **primary** path is stdlib-only local execution (see top-level `QUICKSTART.md`). This container is an
optional convenience for **reproducible** runs on Podman or Docker.

## Podman (rootless-friendly)

```bash
podman build -t hestiaos-jupiter-demo -f container/Containerfile .
podman run --rm -v "$PWD/reports:/app/reports" hestiaos-jupiter-demo
```

## Docker

```bash
docker build -t hestiaos-jupiter-demo -f container/Containerfile .
docker run --rm -v "$PWD/reports:/app/reports" hestiaos-jupiter-demo
```

The default command runs Stage 0 (environment probe) then Stage 1 (mock A/B benchmark) and writes into
`/app/reports` (mount a volume to collect the reports on the host).

## Notes

```
- The container path is OPTIONAL; stdlib-only local execution remains the primary path.
- No external Python packages (stdlib only). No network access at runtime.
- No secrets. No scheduler/HPC jobs. Effects are sandbox-only / simulated (mock).
- Image base python:3.11-slim is the only external dependency, pulled at BUILD time only.
- Runs as a non-root user (uid 10001), rootless-friendly.
```
