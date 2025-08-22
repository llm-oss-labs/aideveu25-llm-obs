# Workshop Patches

This directory contains the git patches used in the workshop labs. Apply them in sequence as you progress through each lab.

## Patch Application Order

```bash
# Lab 1: Reset to baseline
git apply labs/patches/lab1-reset-to-baseline.patch

# Lab 2: Add basic observability  
git apply labs/patches/lab2-add-basic-observability.patch

# Lab 3: Add full observability stack
git apply labs/patches/lab3-add-full-observability-stack.patch

# Lab 4: Add privacy protection
git apply labs/patches/lab4-add-privacy-protection.patch
```

## Patch Contents

| Patch | Description |
|-------|-------------|
| `lab1-reset-to-baseline.patch` | Removes all observability components, creates clean LLM app baseline |
| `lab2-add-basic-observability.patch` | Adds OpenLIT SDK + OpenTelemetry Collector with debug output |
| `lab3-add-full-observability-stack.patch` | Adds Grafana + Prometheus + Tempo for complete visualization |
| `lab4-add-privacy-protection.patch` | Adds Presidio PII masking for privacy-conscious telemetry |

## Troubleshooting

```bash
# Check if patch can be applied
git apply --check labs/patches/lab2-add-basic-observability.patch

# See what would change without applying
git apply --stat labs/patches/lab3-add-full-observability-stack.patch

# Reset if needed
git reset --hard HEAD && git clean -fd
```