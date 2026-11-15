---
name: suite-infra-cloud-network
description: >-
  Distilled infrastructure, cloud, and network engineering rules: DevOps least-privilege & dry-runs,
  Cloudflare Workers best practices, Homelab/VLAN/Netmiko checks, and Frontend Core Web Vitals.
---

# Infrastructure, Cloud, Network & Frontend Standards

## DevOps & Infrastructure
- Follow least-privilege principles for IAM roles and container capabilities.
- Keep container images minimal (multi-stage builds, alpine/distroless).
- Run dry-runs (`terraform plan`, `kubectl diff`) before applying infrastructure changes.

## Cloudflare Serverless
- Follow production Workers best practices (stream responses, avoid global state).
- Retrieve current Cloudflare docs/bindings schemas before implementing.
- Always validate `wrangler` configuration before running deployments.

## Homelab & Network Engineering
- Validate network topology, subnet masks, and VLAN tagging before committing config changes.
- Test connectivity and interface health nondestructively using Netmiko, `ping`, and `traceroute` baselines.
- Enforce least-privilege firewall rules and isolate management VLANs from untrusted segments.

## Frontend & Web Performance
- Profile Core Web Vitals (LCP, INP, CLS) using Chrome DevTools.
- Use modern Tailwind CSS and semantic accessible HTML elements.
- Optimize bundle sizes and eliminate render-blocking network chains.
