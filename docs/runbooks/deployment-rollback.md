# Deployment Rollback Runbook

## Overview
This runbook provides step-by-step procedures for rolling back failed deployments across all supported deployment strategies (blue-green, canary, rolling, direct).

## When to Use This Runbook
- Deployment health checks are failing
- Error rates have increased significantly post-deployment
- Performance degradation detected
- Critical bugs discovered in production
- Manual rollback requested by stakeholders

## Prerequisites
- Access to ProdSprints AI dashboard
- Appropriate permissions for the affected project
- Understanding of the current deployment strategy
- Ability to access monitoring dashboards

## Automatic Rollback (Preferred)

### 🤖 Health-Based Automatic Rollback
The system automatically triggers rollbacks when:
- Error rate > 5% for 2+ minutes
- P95 latency > 2x baseline for 5+ minutes
- Health check failures > 50% for 1+ minute
- Custom SLO thresholds breached

**No manual intervention required** - system will:
1. Stop traffic to failing version
2. Route traffic back to stable version
3. Generate incident report
4. Send notifications to team

## Manual Rollback Procedures

### 🔵 Blue-Green Rollback
**Target Time**: < 2 minutes

1. **Access Release Dashboard**
   ```
   Navigate to: /projects/{project_id}/release
   Verify current status shows "blue-green" strategy
   ```

2. **Initiate Rollback**
   ```
   Click "Rollback" button
   Select reason: [Health Check Failed | Performance Issue | Bug Report | Manual Request]
   Add description of the issue
   Click "Confirm Rollback"
   ```

3. **Monitor Traffic Switch**
   ```
   Watch traffic metrics in real-time
   Verify 100% traffic routes to previous version
   Confirm error rates return to baseline
   ```

4. **Validate Rollback Success**
   ```
   Check health endpoints: GET /health, /ready
   Verify application functionality
   Confirm monitoring shows stable metrics
   ```

### 🕯️ Canary Rollback
**Target Time**: < 3 minutes

1. **Assess Canary Status**
   ```
   Check current canary percentage
   Review health metrics for canary traffic
   Identify specific failure symptoms
   ```

2. **Stop Canary Progression**
   ```
   Click "Pause Release" if still progressing
   Navigate to rollback options
   Select "Rollback to Stable"
   ```

3. **Execute Rollback**
   ```
   Confirm rollback action
   Monitor traffic shift: Canary % → 0%
   Verify stable version handles 100% traffic
   ```

4. **Post-Rollback Validation**
   ```
   Run smoke tests on stable version
   Check error rates and latency
   Verify user-facing functionality
   ```

### 🔄 Rolling Rollback
**Target Time**: < 5 minutes

1. **Identify Failed Instances**
   ```
   Check which instances are unhealthy
   Note the rollout progress percentage
   Determine impact scope
   ```

2. **Halt Rolling Update**
   ```
   Stop the rolling deployment
   Prevent additional instances from updating
   Assess current state
   ```

3. **Revert Instances**
   ```
   Roll back updated instances to previous version
   Restart instances with stable configuration
   Verify each instance health before proceeding
   ```

4. **Validate Full Rollback**
   ```
   Confirm all instances running stable version
   Check load balancer health checks
   Verify application performance
   ```

### ⚡ Direct Rollback
**Target Time**: < 3 minutes

1. **Immediate Revert**
   ```
   Deploy previous stable version
   Update configuration to stable state
   Restart application services
   ```

2. **Service Restoration**
   ```
   Verify services are running
   Check database connectivity
   Confirm external integrations
   ```

3. **Traffic Validation**
   ```
   Test critical user paths
   Verify API endpoints respond correctly
   Check error rates and performance
   ```

## Emergency Procedures

### 🚨 Critical System Failure
If normal rollback procedures fail:

1. **Immediate Actions**
   ```bash
   # Emergency traffic routing
   kubectl patch service app-service -p '{"spec":{"selector":{"version":"stable"}}}'
   
   # Scale down failed version
   kubectl scale deployment app-canary --replicas=0
   
   # Scale up stable version
   kubectl scale deployment app-stable --replicas=5
   ```

2. **Database Rollback (if needed)**
   ```bash
   # Revert database migrations
   alembic downgrade -1
   
   # Restore from backup (last resort)
   pg_restore -d app_db backup_pre_deployment.sql
   ```

3. **Infrastructure Rollback**
   ```bash
   # Terraform rollback
   terraform plan -target=module.app
   terraform apply -target=module.app
   ```

### 🔧 Troubleshooting Common Issues

#### Rollback Stuck or Slow
```bash
# Check deployment status
kubectl get deployments
kubectl describe deployment app-stable

# Force pod recreation
kubectl delete pods -l app=myapp,version=canary

# Check resource constraints
kubectl top nodes
kubectl top pods
```

#### Database Connection Issues
```bash
# Check database connectivity
kubectl exec -it app-pod -- pg_isready -h db-host

# Verify connection pool
kubectl logs deployment/app-stable | grep "database"

# Check database locks
SELECT * FROM pg_locks WHERE NOT granted;
```

#### Load Balancer Issues
```bash
# Check service endpoints
kubectl get endpoints app-service

# Verify ingress configuration
kubectl describe ingress app-ingress

# Test direct pod access
kubectl port-forward pod/app-stable-xxx 8080:8080
```

## Post-Rollback Actions

### 📊 Immediate Validation (0-15 minutes)
- [ ] Verify error rates < 1%
- [ ] Confirm P95 latency within baseline
- [ ] Test critical user journeys
- [ ] Check external service integrations
- [ ] Validate monitoring and alerting

### 📝 Documentation (15-60 minutes)
- [ ] Update incident timeline
- [ ] Document rollback steps taken
- [ ] Record lessons learned
- [ ] Update runbook if needed
- [ ] Notify stakeholders of resolution

### 🔍 Root Cause Analysis (1-24 hours)
- [ ] Analyze deployment logs
- [ ] Review code changes in failed deployment
- [ ] Identify contributing factors
- [ ] Create action items for prevention
- [ ] Schedule postmortem meeting

### 🛠️ Prevention Measures
- [ ] Update deployment tests
- [ ] Enhance monitoring coverage
- [ ] Improve rollback automation
- [ ] Review deployment process
- [ ] Update documentation

## Monitoring and Alerts

### 📈 Key Metrics to Watch
- **Error Rate**: Should return to < 1% within 5 minutes
- **Response Time**: P95 should return to baseline within 3 minutes
- **Throughput**: RPS should stabilize within 2 minutes
- **Health Checks**: All endpoints should return 200 OK

### 🚨 Alert Conditions
- Rollback completion notification
- Error rate normalization alert
- Performance recovery confirmation
- Health check restoration alert

## Escalation

### 📞 When to Escalate
- Rollback fails to complete within target time
- Error rates remain elevated after rollback
- Database corruption suspected
- Multiple services affected
- Customer impact continues

### 👥 Escalation Contacts
1. **Platform Engineering Lead**: @platform-lead
2. **Engineering Manager**: @eng-manager  
3. **CTO**: @cto (for P0 incidents)
4. **Customer Success**: @customer-success (for user impact)

## Success Criteria
- ✅ Error rates < 1%
- ✅ P95 latency within 10% of baseline
- ✅ All health checks passing
- ✅ Critical user journeys functional
- ✅ Monitoring shows stable metrics
- ✅ No active alerts related to the deployment

---

**Last Updated**: 2024-01-01  
**Next Review**: 2024-02-01  
**Owner**: Platform Engineering Team
