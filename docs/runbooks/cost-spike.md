# Cost Spike Investigation Runbook

## Overview
This runbook provides procedures for investigating and responding to unexpected cost increases in cloud infrastructure and services.

## When to Use This Runbook
- Budget alert triggered (>80% of monthly budget)
- Cost increase >20% week-over-week
- Unexpected charges appear in billing
- Resource utilization alerts
- Customer reports of unexpected bills

## Immediate Response (0-30 minutes)

### 🚨 Emergency Cost Controls
If costs are spiking rapidly (>$100/hour increase):

1. **Enable Cost Alerts**
   ```bash
   # Set emergency spending limits
   aws budgets create-budget --budget '{
     "BudgetName": "Emergency-Limit",
     "BudgetLimit": {"Amount": "1000", "Unit": "USD"},
     "TimeUnit": "DAILY",
     "BudgetType": "COST"
   }'
   ```

2. **Check for Runaway Resources**
   ```bash
   # List expensive running instances
   aws ec2 describe-instances --query 'Reservations[].Instances[?State.Name==`running`].[InstanceId,InstanceType,LaunchTime]' --output table
   
   # Check for large storage volumes
   aws ec2 describe-volumes --query 'Volumes[?Size>`100`].[VolumeId,Size,State]' --output table
   
   # Identify high-cost services
   aws ce get-dimension-values --dimension SERVICE --time-period Start=2024-01-01,End=2024-01-31
   ```

3. **Stop Non-Critical Resources**
   ```bash
   # Stop development/staging instances
   aws ec2 stop-instances --instance-ids $(aws ec2 describe-instances --filters "Name=tag:Environment,Values=dev,staging" --query 'Reservations[].Instances[].InstanceId' --output text)
   
   # Scale down auto-scaling groups
   aws autoscaling update-auto-scaling-group --auto-scaling-group-name dev-asg --min-size 0 --desired-capacity 0
   ```

## Investigation Process (30-120 minutes)

### 📊 Cost Analysis Dashboard
1. **Access Cost Dashboard**
   ```
   Navigate to: /enterprise/{project_id}/cost/analyze
   Set time period to last 7 days
   Review cost breakdown by service
   ```

2. **Identify Top Cost Drivers**
   ```
   Check "Top Cost Drivers" section
   Note services with >20% increase
   Review usage metrics for anomalies
   ```

3. **Compare Historical Trends**
   ```
   Switch to 30-day view
   Identify when cost increase began
   Correlate with deployment timeline
   ```

### 🔍 Service-Specific Investigation

#### Compute Costs (EC2, ECS, Lambda)
```bash
# Check instance utilization
aws cloudwatch get-metric-statistics --namespace AWS/EC2 --metric-name CPUUtilization --dimensions Name=InstanceId,Value=i-1234567890abcdef0 --start-time 2024-01-01T00:00:00Z --end-time 2024-01-01T23:59:59Z --period 3600 --statistics Average

# Review auto-scaling events
aws autoscaling describe-scaling-activities --auto-scaling-group-name prod-asg --max-items 50

# Check Lambda invocations
aws logs filter-log-events --log-group-name /aws/lambda/function-name --start-time 1640995200000 --filter-pattern "REPORT"
```

#### Storage Costs (S3, EBS, RDS)
```bash
# Analyze S3 storage classes
aws s3api list-objects-v2 --bucket my-bucket --query 'Contents[?Size>`1000000`].[Key,Size,StorageClass]' --output table

# Check EBS snapshots
aws ec2 describe-snapshots --owner-ids self --query 'Snapshots[?VolumeSize>`100`].[SnapshotId,VolumeSize,StartTime]' --output table

# Review RDS instance sizes
aws rds describe-db-instances --query 'DBInstances[].[DBInstanceIdentifier,DBInstanceClass,AllocatedStorage]' --output table
```

#### Network Costs (Data Transfer, NAT Gateway)
```bash
# Check NAT Gateway usage
aws ec2 describe-nat-gateways --query 'NatGateways[].[NatGatewayId,State,VpcId]' --output table

# Review CloudFront usage
aws cloudfront get-distribution-config --id DISTRIBUTION_ID

# Check data transfer metrics
aws cloudwatch get-metric-statistics --namespace AWS/EC2 --metric-name NetworkOut --start-time 2024-01-01T00:00:00Z --end-time 2024-01-01T23:59:59Z --period 3600 --statistics Sum
```

### 📈 Usage Pattern Analysis

1. **Deployment Correlation**
   ```bash
   # Check recent deployments
   kubectl get deployments --all-namespaces -o wide
   
   # Review scaling events
   kubectl get hpa --all-namespaces
   
   # Check resource requests/limits
   kubectl top pods --all-namespaces --sort-by=cpu
   ```

2. **Traffic Analysis**
   ```bash
   # Check ingress traffic
   kubectl logs -n ingress-nginx deployment/nginx-ingress-controller | grep -E "POST|GET" | tail -1000
   
   # Review load balancer metrics
   aws elbv2 describe-target-health --target-group-arn arn:aws:elasticloadbalancing:region:account:targetgroup/my-targets/1234567890123456
   ```

3. **Database Usage**
   ```sql
   -- Check database connections
   SELECT count(*) FROM pg_stat_activity;
   
   -- Review query performance
   SELECT query, calls, total_time, mean_time 
   FROM pg_stat_statements 
   ORDER BY total_time DESC 
   LIMIT 10;
   
   -- Check database size
   SELECT pg_size_pretty(pg_database_size('mydb'));
   ```

## Common Cost Spike Scenarios

### 🚀 Auto-Scaling Gone Wrong
**Symptoms**: Sudden increase in compute costs, high instance count
**Investigation**:
```bash
# Check scaling policies
aws autoscaling describe-policies --auto-scaling-group-name prod-asg

# Review CloudWatch alarms
aws cloudwatch describe-alarms --state-value ALARM

# Check scaling history
aws autoscaling describe-scaling-activities --auto-scaling-group-name prod-asg --max-items 20
```

**Resolution**:
```bash
# Update scaling policies
aws autoscaling put-scaling-policy --policy-name scale-up --auto-scaling-group-name prod-asg --scaling-adjustment 1 --adjustment-type ChangeInCapacity --cooldown 300

# Set maximum instance limits
aws autoscaling update-auto-scaling-group --auto-scaling-group-name prod-asg --max-size 10
```

### 💾 Storage Explosion
**Symptoms**: Rapid increase in storage costs, large volumes
**Investigation**:
```bash
# Find large files
find /var/log -type f -size +100M -exec ls -lh {} \;

# Check disk usage
df -h
du -sh /var/* | sort -hr

# Review backup retention
aws rds describe-db-snapshots --db-instance-identifier mydb --query 'DBSnapshots[?SnapshotCreateTime<=`2024-01-01`]'
```

**Resolution**:
```bash
# Clean up old logs
find /var/log -name "*.log" -mtime +7 -delete

# Implement log rotation
logrotate -f /etc/logrotate.conf

# Delete old snapshots
aws rds delete-db-snapshot --db-snapshot-identifier old-snapshot
```

### 🌐 Data Transfer Surge
**Symptoms**: High network costs, increased bandwidth usage
**Investigation**:
```bash
# Check CloudFront logs
aws logs filter-log-events --log-group-name /aws/cloudfront/distribution --filter-pattern "[timestamp, request_id, client_ip, method, uri, status, bytes > 1000000]"

# Review API Gateway usage
aws apigateway get-usage --usage-plan-id plan-id --key-id key-id --start-date 2024-01-01 --end-date 2024-01-31

# Check database replication
aws rds describe-db-instances --query 'DBInstances[?ReadReplicaDBInstanceIdentifiers!=`null`]'
```

**Resolution**:
```bash
# Enable CloudFront caching
aws cloudfront update-distribution --id DISTRIBUTION_ID --distribution-config file://distribution-config.json

# Implement API rate limiting
aws apigateway update-usage-plan --usage-plan-id plan-id --patch-ops op=replace,path=/throttle/rateLimit,value=1000

# Optimize database queries
# Review and optimize slow queries identified in investigation
```

## Cost Optimization Actions

### 💡 Immediate Optimizations
1. **Right-size Resources**
   ```bash
   # Downgrade oversized instances
   aws ec2 modify-instance-attribute --instance-id i-1234567890abcdef0 --instance-type t3.medium
   
   # Reduce RDS instance size
   aws rds modify-db-instance --db-instance-identifier mydb --db-instance-class db.t3.micro --apply-immediately
   ```

2. **Implement Reserved Instances**
   ```bash
   # Purchase reserved instances for stable workloads
   aws ec2 purchase-reserved-instances-offering --reserved-instances-offering-id offering-id --instance-count 2
   ```

3. **Enable Spot Instances**
   ```bash
   # Update launch template for spot instances
   aws ec2 modify-launch-template --launch-template-id lt-12345 --version-description "Enable spot instances"
   ```

### 📊 Long-term Optimizations
1. **Implement Cost Monitoring**
   ```yaml
   # Add to monitoring stack
   - alert: HighCostIncrease
     expr: increase(aws_billing_estimated_charges[1h]) > 50
     for: 5m
     labels:
       severity: warning
     annotations:
       summary: "Cost increase detected"
   ```

2. **Set Up Budget Alerts**
   ```bash
   # Create detailed budget alerts
   aws budgets create-budget --budget file://budget-config.json --notifications-with-subscribers file://notifications.json
   ```

3. **Automate Resource Cleanup**
   ```bash
   # Schedule cleanup jobs
   cat > cleanup-cron.yaml << EOF
   apiVersion: batch/v1
   kind: CronJob
   metadata:
     name: resource-cleanup
   spec:
     schedule: "0 2 * * *"
     jobTemplate:
       spec:
         template:
           spec:
             containers:
             - name: cleanup
               image: cleanup-script:latest
               command: ["/cleanup.sh"]
   EOF
   ```

## Prevention Measures

### 🛡️ Cost Controls
1. **Implement Spending Limits**
   - Set up AWS Budgets with alerts at 50%, 80%, 100%
   - Configure billing alarms in CloudWatch
   - Enable cost anomaly detection

2. **Resource Tagging Strategy**
   ```bash
   # Tag all resources for cost allocation
   aws ec2 create-tags --resources i-1234567890abcdef0 --tags Key=Project,Value=prodsprints Key=Environment,Value=prod Key=Owner,Value=platform-team
   ```

3. **Automated Policies**
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Deny",
         "Action": [
           "ec2:RunInstances"
         ],
         "Resource": "*",
         "Condition": {
           "StringNotEquals": {
             "ec2:InstanceType": [
               "t3.micro",
               "t3.small",
               "t3.medium"
             ]
           }
         }
       }
     ]
   }
   ```

### 📈 Monitoring and Alerting
1. **Cost Dashboard Setup**
   - Daily cost tracking by service
   - Week-over-week comparison
   - Budget utilization percentage
   - Top cost drivers identification

2. **Automated Responses**
   ```bash
   # Auto-stop expensive resources
   aws events put-rule --name "StopExpensiveInstances" --schedule-expression "rate(1 hour)"
   aws events put-targets --rule "StopExpensiveInstances" --targets "Id"="1","Arn"="arn:aws:lambda:region:account:function:cost-control"
   ```

## Communication

### 📢 Stakeholder Notification
```markdown
**Cost Spike Alert - [Project Name]**

**Summary**: Detected X% cost increase over Y period
**Impact**: $Z additional spend
**Root Cause**: [Brief description]
**Actions Taken**: [List of immediate actions]
**ETA for Resolution**: [Timeline]
**Next Update**: [When you'll provide next update]

**Contact**: @platform-team for questions
```

### 📊 Executive Summary
- Current month spend vs. budget
- Identified root cause
- Immediate cost savings achieved
- Long-term prevention measures
- Revised budget forecast

## Success Criteria
- ✅ Cost increase identified and contained
- ✅ Root cause determined and documented
- ✅ Immediate optimizations implemented
- ✅ Long-term prevention measures in place
- ✅ Stakeholders notified and updated
- ✅ Budget forecast updated

---

**Last Updated**: 2024-01-01  
**Next Review**: 2024-02-01  
**Owner**: Platform Engineering Team
