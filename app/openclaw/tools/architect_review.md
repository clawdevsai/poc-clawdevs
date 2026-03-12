# TOOLS / ARCHITECT-REVIEW

Primary tools:
- openclaw.sessions.send
- redis.publish_pr_review
- redis.publish_deploy_event

Operational policy:
- Emit explicit final arbitration outcome for escalated rounds.
