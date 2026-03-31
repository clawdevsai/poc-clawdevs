# Troubleshooting

## Hook Not Triggering

**Problem**: `before_execution` hook not being called

**Solutions**:
1. Check manifest.json has hooks registered
2. Verify hook handler name matches implementation
3. Check event name is correct (before_execution vs before_impl)
4. Review agent configuration

## Low Test Coverage

**Problem**: Coverage below 80% target

**Solutions**:
1. Write unit tests for each decision path
2. Add integration tests for hooks
3. Test error handling paths
4. Review untested utility functions

## Recommendation Not Matching Requirements

**Problem**: Hook returns wrong tech stack suggestion

**Solutions**:
1. Check requirement parsing (conversation → config → system_prompt)
2. Verify regex patterns for requirement detection
3. Review decision matrix mappings
4. Test with explicit requirements in config

## Performance Bottleneck

**Problem**: Implementation doesn't meet latency requirements

**Solutions**:
1. Review chosen tech stack for requirements
2. Consider caching strategy (Redis)
3. Profile code for hot spots
4. Validate database queries
5. Review scaling architecture

## Build or Test Failures

**Problem**: Tests or builds failing after implementation

**Solutions**:
1. Run full test suite (npm test / pytest / go test)
2. Check for missing dependencies
3. Verify type checking (tsc)
4. Review linting errors
5. Check security scan results
