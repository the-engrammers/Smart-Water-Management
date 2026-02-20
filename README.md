# Smart Water Management

## Phase 1 Status: Monitoring ✅

The live monitoring stack is now integrated and ready for team use:
- Streamlit dashboard for live leak visibility ([frontend/app.py](frontend/app.py))
- Alert simulation service with CSV logging ([backend/alert_service.py](backend/alert_service.py))
- Project hygiene via `.gitignore` to exclude runtime/cache files

### Demo Run Commands

```bash
# Terminal 1
cd frontend
streamlit run app.py

# Terminal 2
cd ..
python backend/alert_service.py
```

## Phase 2 Assignments

### Member 5 — Implement Decision Support UI & Farmer Controls
- Add `Smart Action Box` showing AI decision and reason
- Add `START/STOP PUMP` controls on dashboard
- Add `Water Saved` optimization metric/chart vs traditional irrigation

### Member 7 — Implement Intelligence Logic (Rules Engine)
- Build irrigation decision logic based on Operations Research rules
- Expose decision variables for Member 5 UI integration
- Provide decision payload (action, reason, confidence/timing)

## Dashboard Evidence (Monitoring Phase)

Add the latest dashboard screenshot here after each validated demo run:
- Suggested path: `docs/images/monitoring-phase-dashboard.png`

