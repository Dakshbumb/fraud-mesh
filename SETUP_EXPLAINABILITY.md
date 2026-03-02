# Setup: Threshold Explainability Feature

## Quick Setup

### 1. Install Frontend Dependencies

```bash
cd frontend
npm install
```

This will install the new `lucide-react` package for icons in the audit trail component.

### 2. Verify Backend Files

Make sure these new files exist:
- `backend/threshold_explainer.py` ✅
- `frontend/src/components/ThresholdAuditTrail.jsx` ✅

### 3. Start the System

```bash
# Terminal 1: Backend
cd backend
python main.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 4. Open Browser

Navigate to: `http://localhost:5173`

### 5. Wait 30 Seconds

Let the system generate some threshold decisions so you have data to show.

---

## What You'll See

### New Component: Threshold Decision Audit Trail

Located at the bottom of the dashboard, below the Fairness Panel.

**Features:**
- Real-time feed of threshold decisions
- Expandable cards with complete explanations
- Filter by adjustment magnitude (All, Major, Moderate, Minor)
- Export complete audit trail to JSON

**Each Decision Shows:**
- Decision ID and timestamp
- Primary reason for adjustment
- Detailed step-by-step explanation
- Risk context
- All adjustment factors (time, amount, network, FPR, fairness)
- Transaction context (amount, time, fraud rate, FPR)
- Sensitivity level (HIGH, MEDIUM, LOW)
- Adjustment magnitude (MAJOR, MODERATE, MINOR, NONE)

---

## API Endpoints Added

### GET /api/threshold-audit-trail

Returns recent threshold decisions with explanations.

**Query Parameters:**
- `count` (optional): Number of decisions to return (default: 50)

**Response:**
```json
{
  "decisions": [...],
  "summary": {
    "total_decisions": 150,
    "avg_threshold": 0.48,
    "sensitivity_distribution": {...},
    "adjustment_distribution": {...}
  },
  "current_threshold": 0.48
}
```

### POST /api/threshold-audit-trail/export

Exports complete audit trail to JSON file.

**Response:**
```json
{
  "success": true,
  "filepath": "threshold_audit_trail_20240115_223045.json",
  "message": "Audit trail exported successfully"
}
```

---

## Testing the Feature

### 1. Check Audit Trail is Populating

- Open browser to `http://localhost:5173`
- Scroll to bottom of page
- Look for "Threshold Decision Audit Trail" component
- Should see decisions appearing every few seconds

### 2. Expand a Decision

- Click on any decision card
- Should expand to show:
  - Risk context
  - Detailed explanation
  - Adjustment factors
  - Transaction context

### 3. Test Filtering

- Click "Major" button
- Should only show major adjustments
- Click "All" to see everything again

### 4. Test Export

- Click "Export Complete Audit Trail (JSON)" button
- Check browser console for confirmation
- (Note: Full export functionality requires backend file write permissions)

---

## Troubleshooting

### Issue: Audit trail is empty

**Solution:**
- Wait 30 seconds for transactions to process
- Check backend console for errors
- Verify `threshold_explainer` is initialized in `main.py`

### Issue: Icons not showing

**Solution:**
```bash
cd frontend
npm install lucide-react
```

### Issue: Component not rendering

**Solution:**
- Check browser console for errors
- Verify `ThresholdAuditTrail` is imported in `App.jsx`
- Verify component is added to the layout

### Issue: API endpoint returns 500 error

**Solution:**
- Check backend console for Python errors
- Verify `threshold_explainer.py` has no syntax errors
- Restart backend server

---

## Demo Checklist

Before showing to judges:

- [ ] Backend is running without errors
- [ ] Frontend is running without errors
- [ ] System has been running for at least 30 seconds
- [ ] Audit trail shows at least 10 decisions
- [ ] Can expand decision cards successfully
- [ ] Filters work (All, Major, Moderate, Minor)
- [ ] Current threshold value is displayed
- [ ] No console errors in browser

---

## Key Files Modified

### Backend
- `backend/threshold_explainer.py` (NEW)
- `backend/main.py` (MODIFIED - added explainer integration and API endpoints)

### Frontend
- `frontend/src/components/ThresholdAuditTrail.jsx` (NEW)
- `frontend/src/App.jsx` (MODIFIED - added component and state)
- `frontend/package.json` (MODIFIED - added lucide-react)

### Documentation
- `THRESHOLD_EXPLAINABILITY_PROOF.md` (NEW)
- `DEMO_SCRIPT_EXPLAINABILITY.md` (NEW)
- `SETUP_EXPLAINABILITY.md` (NEW - this file)

---

## Next Steps

1. **Test the feature** - Make sure everything works
2. **Review the demo script** - Read `DEMO_SCRIPT_EXPLAINABILITY.md`
3. **Practice the demo** - Run through it 2-3 times
4. **Prepare for questions** - Review the Q&A section in the demo script

---

## Success Criteria

You're ready to demo when:

✅ Audit trail is visible and populating
✅ Decision cards expand to show full details
✅ All adjustment factors are displayed
✅ Explanations are human-readable
✅ Export button is visible
✅ No errors in console

---

## Contact

If you encounter issues, check:
1. Backend console for Python errors
2. Browser console for JavaScript errors
3. Network tab for API call failures
