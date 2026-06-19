# Comprehensive Project Integrity Check Specification

## Feature Request
Perform a comprehensive, end-to-end full project integrity check across both 'frontend/' and 'backend/' directories. 

Please systematically verify the following 4 pillars:
1. BACKEND ROUTING: Ensure the Express server in backend/src/main.ts handles both /metrics and /api/v1/metrics cleanly, with proper logging to security-audit.log and correct conditional cases for 'Vardhaman' and 'SecureLogix Labs'.
2. FRONTEND COMPACTNESS: Check frontend/src/App.tsx to ensure the layout is strictly constrained within 100vh viewport height (max-h-screen) with zero duplicated central orbs and proper layout alignment.
3. VOICE & SYNC INTEGRATION: Verify that Web Speech API speech recognition triggers dropdown updates and fetches correct backend states synchronously without connection errors.
4. SYNTAX & TYPES: Perform a clean typescript verification to ensure no missing variables, dangling unclosed tags, or compilation breaks exist.

Generate a master verification report in .pipeline/final-audit.md and deliver the final verdict.

## Files to Modify
- None (this is a verification task)

## Files to Create
- `.pipeline/final-audit.md` - Master verification report

## Implementation Details

### Pillar 1: BACKEND ROUTING
- Verify backend/src/main.ts has proper /metrics endpoint (root level)
- Verify backend/src/main.ts has proper /api/v1/metrics endpoint 
- Check that both endpoints handle vendor query parameter correctly
- Verify logging to security-audit.log works for both endpoints
- Confirm conditional logic for 'Vardhaman' (sets frozen: true) and 'SecureLogix Labs' (returns specific metrics)
- Ensure no routing conflicts or errors

### Pillar 2: FRONTEND COMPACTNESS
- Check frontend/src/App.tsx uses height: '100vh' or equivalent max-h-screen constraint
- Verify layout uses CSS Grid or Flexbox to fit within viewport
- Ensure no duplicated central orb structures (only one Forensic Orb)
- Check proper alignment of metrics matrix, stream logs, and control elements
- Confirm no overflow causing vertical scrollbars

### Pillar 3: VOICE & SYNC INTEGRATION
- Verify Web Speech API is properly initialized in frontend/src/App.tsx
- Check that speech recognition updates selectedVendorName state
- Confirm that state change triggers fetchMetrics and fetchLiveLogs
- Verify no connection errors occur during synchronous state updates
- Ensure dropdown and speech recognition stay in sync

### Pillar 4: SYNTAX & TYPES
- Run TypeScript compilation on both frontend and backend
- Check for any missing variables, undefined types, or syntax errors
- Verify all JSX tags are properly closed
- Ensure no dangling references or unused variables cause issues
- Confirm clean build with no errors

## Success Criteria
- All 4 pillars pass verification
- Master verification report generated in .pipeline/final-audit.md
- Final verdict delivered based on audit results