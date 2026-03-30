# Skill: analyze_metrics

## Purpose
Analyze PostgreSQL metrics against detection rules to identify database health issues, trigger alerts, and escalate critical findings to appropriate teams.

## Input Parameters

### Required Inputs
- `connection_pool`: Connection pool metrics object
  - `current_connections`: Number of active connections (integer)
  - `max_connections`: Maximum configured connections (integer)
  - `idle_connections`: Number of idle connections (integer)
  - `waiting_connections`: Number of waiting connections (integer)

- `slow_queries`: Array of slow query objects
  - `query_text`: SQL query (string)
  - `execution_time_ms`: Execution duration in milliseconds (number)
  - `frequency`: Times executed in window (number)
  - `last_executed`: ISO timestamp of last execution (string)

- `disk_metrics`: Disk space metrics object
  - `total_gb`: Total disk space (number)
  - `used_gb`: Used disk space (number)
  - `available_gb`: Available disk space (number)
  - `mount_point`: Database data directory mount (string)

- `config_thresholds`: Detection rule thresholds object
  - `connection_pool_warning_percent`: Warning threshold % (default: 80)
  - `connection_pool_critical_percent`: Critical threshold % (default: 95)
  - `slow_queries_warning_count`: Warning threshold count (default: 3)
  - `disk_critical_gb`: Critical threshold GB (default: 5)
  - `disk_warning_gb`: Warning threshold GB (default: 10)
  - `index_fragmentation_warning_percent`: Warning threshold % (default: 30)

### Optional Inputs
- `index_metrics`: Index fragmentation metrics (optional)
  - `total_indexes`: Total indexes in database (number)
  - `fragmented_indexes`: Indexes above fragmentation threshold (array)
  - `max_fragmentation_percent`: Highest fragmentation level (number)

- `context`: Analysis context from agent memory
  - `previous_alerts`: Recent alerts for deduplication (array)
  - `baseline_metrics`: Historical baseline for comparison (object)
  - `escalation_history`: Recent escalations to avoid noise (array)

## Output Structure

```json
{
  "analysis_timestamp": "ISO 8601 timestamp",
  "summary": {
    "health_status": "healthy|warning|critical",
    "issues_detected": 0,
    "escalations_required": 0,
    "recommendations": []
  },
  "activity_events": [
    {
      "event_id": "unique identifier",
      "timestamp": "ISO 8601",
      "category": "connection_pool|slow_query|disk_space|index_fragmentation|configuration",
      "severity": "info|warning|critical",
      "title": "Event title",
      "description": "Detailed description",
      "metric_name": "Specific metric",
      "metric_value": "Current value",
      "threshold_value": "Threshold value",
      "rule_name": "Matching rule ID"
    }
  ],
  "memory_updates": [
    {
      "memory_key": "Key path in agent memory",
      "value": "Value to store",
      "timestamp": "ISO 8601",
      "ttl_seconds": "Cache duration or null for permanent"
    }
  ],
  "escalations": [
    {
      "escalation_id": "Unique identifier",
      "timestamp": "ISO 8601",
      "severity": "critical|high",
      "target": "architect|platform_team|dba_team",
      "title": "Escalation title",
      "description": "Issue description",
      "affected_component": "database|connection_pool|disk_storage",
      "recommended_actions": [
        "Action 1",
        "Action 2"
      ]
    }
  ]
}
```

## Detection Rules

```yaml
rules:
  # CONNECTION POOL RULES
  - name: "db_connection_pool_warning"
    id: "cp_warning_80"
    category: "connection_pool"
    condition: "pool_utilization_percent > 80%"
    severity: "warning"
    actions:
      - log_event
      - update_memory: "db.connection_pool.utilization_percent"
    description: "Connection pool utilization exceeds 80% threshold"
    threshold_percent: 80
    recommendation: "Monitor connection pool; consider connection pooling optimization or increasing max_connections"
    escalate: false

  - name: "db_connection_pool_critical"
    id: "cp_critical_95"
    category: "connection_pool"
    condition: "pool_utilization_percent >= 95%"
    severity: "critical"
    actions:
      - log_event
      - update_memory: "db.connection_pool.utilization_percent"
      - escalate_to_architect
      - escalate_to_platform_team
    description: "Connection pool utilization at or exceeds 95% critical threshold"
    threshold_percent: 95
    recommendation: "URGENT: Connection pool near saturation. Investigate slow connections, terminate idle sessions, or scale connection pool immediately."
    escalate: true
    escalation_priority: "P1"

  - name: "db_connection_pool_saturated"
    id: "cp_saturated_100"
    category: "connection_pool"
    condition: "current_connections >= max_connections"
    severity: "critical"
    actions:
      - log_event
      - escalate_to_architect
      - escalate_to_platform_team
      - escalate_to_dba_team
    description: "Connection pool completely saturated; new connections cannot be established"
    recommendation: "CRITICAL: Immediate action required. System cannot accept new database connections. Kill idle connections or restart services."
    escalate: true
    escalation_priority: "P0_critical"

  # SLOW QUERY RULES
  - name: "db_slow_query_single"
    id: "sq_warning_single"
    category: "slow_query"
    condition: "execution_time_ms > 5000 ms"
    severity: "info"
    actions:
      - log_event
      - update_memory: "db.slow_queries.recent"
    description: "Single query execution time exceeds 5000ms threshold"
    threshold_ms: 5000
    recommendation: "Review query execution plan; consider adding indexes or optimizing query logic"
    escalate: false

  - name: "db_slow_queries_multiple"
    id: "sq_warning_multiple"
    category: "slow_query"
    condition: "slow_query_count > 3 in 5-minute window"
    severity: "warning"
    actions:
      - log_event
      - update_memory: "db.slow_queries.count_5min"
      - update_memory: "db.slow_queries.recent"
    description: "Multiple slow queries detected; > 3 queries in 5-minute window"
    threshold_count: 3
    recommendation: "Monitor slow queries; profile queries and execution plans; consider query optimization"
    escalate: false

  - name: "db_slow_queries_cascading"
    id: "sq_critical_cascading"
    category: "slow_query"
    condition: "slow_query_count >= 5 in 5-minute window AND average_execution_time > 3000ms"
    severity: "critical"
    actions:
      - log_event
      - update_memory: "db.slow_queries.count_5min"
      - update_memory: "db.slow_queries.cascade_detected"
      - escalate_to_architect
      - escalate_to_dba_team
    description: "Cascading slow query event; >= 5 queries with high execution times"
    threshold_count: 5
    threshold_ms: 3000
    recommendation: "URGENT: Multiple slow queries detected. Database may be under load or experiencing query plan issues. Investigate immediately."
    escalate: true
    escalation_priority: "P1"

  # DISK SPACE RULES
  - name: "db_disk_space_warning"
    id: "ds_warning_10gb"
    category: "disk_space"
    condition: "available_gb < 10"
    severity: "warning"
    actions:
      - log_event
      - update_memory: "db.disk.available_gb"
      - update_memory: "db.disk.growth_rate_gb_per_hour"
    description: "Available disk space below 10GB warning threshold"
    threshold_gb: 10
    recommendation: "Monitor disk space growth; plan storage expansion; clean up old WAL files or logs if safe"
    escalate: false

  - name: "db_disk_space_critical"
    id: "ds_critical_5gb"
    category: "disk_space"
    condition: "available_gb < 5"
    severity: "critical"
    actions:
      - log_event
      - update_memory: "db.disk.available_gb"
      - update_memory: "db.disk.growth_rate_gb_per_hour"
      - escalate_to_architect
      - escalate_to_platform_team
      - escalate_to_dba_team
    description: "Available disk space below 5GB critical threshold; database may fail soon"
    threshold_gb: 5
    recommendation: "CRITICAL: Disk space critically low. Database operations may fail. Immediate storage expansion required."
    escalate: true
    escalation_priority: "P0_critical"

  - name: "db_disk_space_exhausted"
    id: "ds_exhausted_1gb"
    category: "disk_space"
    condition: "available_gb < 1"
    severity: "critical"
    actions:
      - log_event
      - escalate_to_architect
      - escalate_to_platform_team
      - escalate_to_dba_team
    description: "Disk space critically exhausted; < 1GB remaining"
    threshold_gb: 1
    recommendation: "CRITICAL EMERGENCY: Disk space almost exhausted. Database may stop accepting writes. Emergency storage expansion required immediately."
    escalate: true
    escalation_priority: "P0_emergency"

  # INDEX FRAGMENTATION RULES
  - name: "db_index_fragmentation_warning"
    id: "if_warning_30pct"
    category: "index_fragmentation"
    condition: "index_fragmentation_percent > 30%"
    severity: "warning"
    actions:
      - log_event
      - update_memory: "db.indexes.fragmentation_percent"
      - update_memory: "db.indexes.fragmented_list"
    description: "Index fragmentation exceeds 30% threshold"
    threshold_percent: 30
    recommendation: "Schedule index maintenance; consider REINDEX of fragmented indexes during maintenance window"
    escalate: false

  - name: "db_index_fragmentation_critical"
    id: "if_critical_50pct"
    category: "index_fragmentation"
    condition: "index_fragmentation_percent > 50%"
    severity: "critical"
    actions:
      - log_event
      - update_memory: "db.indexes.fragmentation_percent"
      - update_memory: "db.indexes.fragmented_list"
      - escalate_to_dba_team
    description: "Index fragmentation critically high; > 50% threshold"
    threshold_percent: 50
    recommendation: "Urgent index maintenance required. Fragmented indexes causing query performance degradation. Schedule REINDEX immediately."
    escalate: true
    escalation_priority: "P2"

  # CONFIGURATION RULES
  - name: "db_config_suboptimal_shared_buffers"
    id: "cfg_warning_shared_buffers"
    category: "configuration"
    condition: "shared_buffers < (total_system_memory * 0.25)"
    severity: "warning"
    actions:
      - log_event
      - update_memory: "db.config.shared_buffers_mb"
    description: "shared_buffers configured below recommended 25% of system memory"
    recommendation: "Consider increasing shared_buffers to improve cache efficiency; requires PostgreSQL restart"
    escalate: false

  - name: "db_config_suboptimal_work_mem"
    id: "cfg_info_work_mem"
    category: "configuration"
    condition: "work_mem < 256MB"
    severity: "info"
    actions:
      - log_event
      - update_memory: "db.config.work_mem_mb"
    description: "work_mem configured below recommended minimum for production"
    recommendation: "Consider increasing work_mem for better sort and hash performance"
    escalate: false

  # REPLICATION RULES (if applicable)
  - name: "db_replication_lag_critical"
    id: "rep_critical_lag"
    category: "replication"
    condition: "replication_lag_seconds >= 60"
    severity: "critical"
    actions:
      - log_event
      - update_memory: "db.replication.lag_seconds"
      - escalate_to_dba_team
    description: "Replication lag exceeds 60 seconds threshold"
    threshold_seconds: 60
    recommendation: "URGENT: Replication lag detected. Investigate standby server performance and network latency."
    escalate: true
    escalation_priority: "P1"
```

## Processing Logic

### Step 1: Metric Collection
1. Normalize incoming metrics to standard units
2. Calculate derived metrics (utilization %, growth rate)
3. Validate metric accuracy and consistency
4. Timestamp all measurements

### Step 2: Rule Evaluation
1. Iterate through all applicable detection rules
2. Evaluate each rule condition against current metrics
3. Track rule matches with severity levels
4. Compare against baseline and historical data

### Step 3: Event Generation
1. Create activity event for each rule match
2. Include metric values, thresholds, and rule details
3. Add contextual information and recommendations
4. Assign unique event identifiers

### Step 4: Memory Updates
1. Store current metric values in agent memory
2. Update trend analysis (growth rates, patterns)
3. Track recent event history for deduplication
4. Store escalation history to avoid alert fatigue

### Step 5: Escalation Determination
1. Identify all critical and high-severity events
2. Check escalation history to avoid duplicates
3. Determine escalation targets based on event type
4. Create escalation records with context

### Step 6: Output Assembly
1. Compile analysis summary
2. Aggregate all activity events
3. Prepare memory update operations
4. Format escalation notifications

## Error Handling

```yaml
error_handling:
  - condition: "Invalid metric format"
    action: "Log error event; skip metric; continue processing remaining metrics"
    severity: "warning"

  - condition: "Missing required threshold"
    action: "Use hardcoded default threshold; log warning"
    severity: "warning"

  - condition: "Database connection fails"
    action: "Log connection error; escalate as potential outage"
    severity: "critical"

  - condition: "Metric value out of expected range"
    action: "Flag as anomaly; log; continue processing"
    severity: "info"
```

## Example Execution Flow

### Input Example
```json
{
  "connection_pool": {
    "current_connections": 38,
    "max_connections": 40,
    "idle_connections": 2,
    "waiting_connections": 5
  },
  "slow_queries": [
    {
      "query_text": "SELECT * FROM large_table WHERE id > 1000000",
      "execution_time_ms": 8500,
      "frequency": 1,
      "last_executed": "2026-03-30T14:35:22Z"
    }
  ],
  "disk_metrics": {
    "total_gb": 100,
    "used_gb": 96,
    "available_gb": 4,
    "mount_point": "/var/lib/postgresql"
  },
  "config_thresholds": {
    "connection_pool_warning_percent": 80,
    "connection_pool_critical_percent": 95,
    "slow_queries_warning_count": 3,
    "disk_critical_gb": 5,
    "disk_warning_gb": 10
  }
}
```

### Output Example
```json
{
  "analysis_timestamp": "2026-03-30T14:36:00Z",
  "summary": {
    "health_status": "critical",
    "issues_detected": 2,
    "escalations_required": 2,
    "recommendations": [
      "URGENT: Connection pool at 95% utilization",
      "CRITICAL: Disk space below 5GB threshold"
    ]
  },
  "activity_events": [
    {
      "event_id": "evt_20260330_143600_001",
      "timestamp": "2026-03-30T14:36:00Z",
      "category": "connection_pool",
      "severity": "critical",
      "title": "Connection Pool Critical Saturation",
      "description": "Connection pool utilization has reached 95% (38 of 40 connections active)",
      "metric_name": "connection_pool_utilization_percent",
      "metric_value": "95%",
      "threshold_value": "95%",
      "rule_name": "db_connection_pool_critical"
    },
    {
      "event_id": "evt_20260330_143600_002",
      "timestamp": "2026-03-30T14:36:00Z",
      "category": "disk_space",
      "severity": "critical",
      "title": "Critical Disk Space Alert",
      "description": "Available disk space has dropped below critical threshold: 4GB of 100GB total",
      "metric_name": "disk_available_gb",
      "metric_value": "4GB",
      "threshold_value": "5GB",
      "rule_name": "db_disk_space_critical"
    }
  ],
  "memory_updates": [
    {
      "memory_key": "db.connection_pool.utilization_percent",
      "value": 95,
      "timestamp": "2026-03-30T14:36:00Z",
      "ttl_seconds": null
    },
    {
      "memory_key": "db.disk.available_gb",
      "value": 4,
      "timestamp": "2026-03-30T14:36:00Z",
      "ttl_seconds": null
    }
  ],
  "escalations": [
    {
      "escalation_id": "esc_20260330_143600_001",
      "timestamp": "2026-03-30T14:36:00Z",
      "severity": "critical",
      "target": "architect",
      "title": "Connection Pool Critical - Immediate Action Required",
      "description": "Database connection pool has reached 95% utilization (38 of 40 connections). System approaching saturation.",
      "affected_component": "connection_pool",
      "recommended_actions": [
        "Review active connections and identify long-running queries",
        "Terminate idle connections if safe",
        "Consider temporary connection pooling optimization",
        "Increase max_connections if capacity allows"
      ]
    },
    {
      "escalation_id": "esc_20260330_143600_002",
      "timestamp": "2026-03-30T14:36:00Z",
      "severity": "critical",
      "target": "platform_team",
      "title": "Critical Disk Space Alert - Storage Expansion Needed",
      "description": "Database disk space has dropped below 5GB critical threshold. Only 4GB available on database mount.",
      "affected_component": "disk_storage",
      "recommended_actions": [
        "Immediately plan and execute storage expansion",
        "Monitor disk usage closely; may fill within hours",
        "Review and clean up old backup or WAL files if safe",
        "Consider archiving unused data if applicable"
      ]
    }
  ]
}
```

## Notes

- All timestamps are ISO 8601 format with timezone
- Metric values should maintain appropriate precision
- Rule conditions are evaluated independently; multiple rules can match
- Escalations are aggregated by target and severity
- Memory updates enable trend analysis and historical context
- No recovery actions are performed; this is detection-only phase
