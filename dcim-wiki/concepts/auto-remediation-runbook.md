---
title: Auto-Remediation Runbook
created: 2026-06-23
updated: 2026-06-23
type: concept
tags: [workflow-automation, sop-runbook]
sources: []
confidence: high
---

# Auto-Remediation Runbook

Auto-remediation procedures untuk DCIM platform.

## Safety Guards

### Pre-Execution Checks
1. Blast radius assessment
2. Impact analysis via [[cmdb]]
3. Time window validation
4. Approval verification

### Execution Guards
1. Rollback capability
2. Timeout limits
3. Circuit breaker
4. Human override

## Common Remediation Scenarios

### Service Restart
```bash
# Check service status
systemctl status dcim-app

# Restart service
systemctl restart dcim-app

# Verify health
curl http://localhost:8080/health
```

### Disk Cleanup
```bash
# Check disk usage
df -h

# Clean logs older than 7 days
find /var/log/dcim -type f -mtime +7 -delete

# Clean temp files
find /tmp -type f -mtime +1 -delete
```

### Memory Relief
```bash
# Check memory usage
free -m

# Clear cache
sync; echo 3 > /proc/sys/vm/drop_caches

# Restart if needed
systemctl restart dcim-app
```

## Monitoring
- Remediation success rate
- Rollback frequency
- Mean time to remediate
- False positive rate

## Escalation
- Failed remediation: Manual intervention
- Rollback failure: Emergency team
- Safety guard trigger: Operations manager

## Related
- [[workflow-automation]]
- [[workflow-state-machine]]
- [[impact-analysis-strategy]]
- [[cmdb]]
- [[workflow-automation-patterns]]
