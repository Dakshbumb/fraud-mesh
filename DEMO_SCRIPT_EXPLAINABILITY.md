# Demo Script: Proving Threshold Explainability

## Addressing Judge's Concern: "It's Just Another Black Box"

---

## Setup (Before Demo)

1. Start backend: `cd backend && python main.py`
2. Start frontend: `cd frontend && npm run dev`
3. Open browser to `http://localhost:5173`
4. Let system run for 30 seconds to generate threshold decisions

---

## Demo Flow (3 Minutes)

### Part 1: Show the Problem (30 seconds)

**Say:**
> "You mentioned the adaptive threshold is a black box. Let me show you why it's actually the opposite."

**Do:**
- Scroll to the **Threshold Meter** component
- Point to the current threshold value (e.g., 0.48)

**Say:**
> "In a black box system, you'd just see this number change with no explanation. But watch this..."

---

### Part 2: Reveal the Audit Trail (1 minute)

**Do:**
- Scroll down to the **Threshold Decision Audit Trail** component
- Point to the header: "Complete transparency - every threshold adjustment explained"

**Say:**
> "Every single threshold adjustment is logged with a complete explanation. Let me show you one."

**Do:**
- Click on the most recent decision card to expand it

**Say:**
> "Here's what happened 5 seconds ago:"

**Point to each section:**

1. **Primary Reason:**
   > "The system tells us in plain English: 'Late-night transaction - increased sensitivity'"

2. **Detailed Explanation:**
   > "Here's the math: started at 0.50, time adjustment -0.10, amount adjustment -0.05, network adjustment -0.15, final threshold 0.40"

3. **Risk Context:**
   > "And here's why: late-night hours, high-value transaction, network under attack"

4. **Adjustment Factors:**
   > "Every single factor is shown numerically. Nothing is hidden."

---

### Part 3: Show Auditability (1 minute)

**Do:**
- Scroll through the audit trail feed
- Point to the filter buttons (All, Major, Moderate, Minor)

**Say:**
> "We can filter by adjustment magnitude to focus on major decisions."

**Do:**
- Click "Major" filter

**Say:**
> "These are the big threshold changes. Each one has a complete explanation."

**Do:**
- Click "Export Complete Audit Trail" button

**Say:**
> "And we can export the entire audit trail as JSON for compliance officers, regulators, or auditors."

---

### Part 4: Contrast with Black Box (30 seconds)

**Say:**
> "Let me be clear about the difference:"

**Black Box:**
- ❌ Threshold changes with no explanation
- ❌ Analysts don't know why
- ❌ No audit trail
- ❌ Can't verify fairness

**Our System (Glass Box):**
- ✅ Every change has a human-readable explanation
- ✅ All factors are numerically documented
- ✅ Complete audit trail with export
- ✅ Fairness adjustments are transparent

**Say:**
> "This isn't a black box. It's a glass box with complete transparency."

---

## Backup: If Judge Asks Questions

### Q: "How do I know these explanations are accurate?"

**A:** 
> "Great question. The explanations are generated directly from the same code that computes the threshold. They're not post-hoc rationalizations - they're the actual logic documented in real-time."

**Show:**
- Open `backend/threshold_explainer.py` in editor
- Point to `_generate_detailed_explanation` method
- Show how it reads the actual adjustment factors from the threshold snapshot

---

### Q: "Can analysts override the threshold?"

**A:**
> "Yes, absolutely. The base threshold is configurable. But more importantly, analysts can now understand WHY the threshold is at a certain value, so they can make informed decisions about whether to adjust it."

---

### Q: "What about the GNN model - isn't that a black box?"

**A:**
> "Good catch. The GNN is a neural network, which is harder to interpret. That's why we:"
> 1. Combine it with rule-based scoring (60% rules, 40% GNN)
> 2. Use Claude to explain the overall fraud decision
> 3. Show which rules triggered in the explanation
> 4. Make the threshold adjustment completely transparent

**Say:**
> "We're not claiming the entire system is perfectly interpretable. But the threshold - which controls sensitivity - is 100% explainable."

---

### Q: "How does this help with production data?"

**A:**
> "When banks use real data, they need to explain decisions to customers and regulators. This audit trail provides:"
> - Documentation for regulatory compliance
> - Explanations for customer disputes
> - Debugging for false positive issues
> - Verification that fairness adjustments are working

---

## Key Talking Points

### 1. Transparency
- Every threshold decision is logged
- All factors are documented
- Nothing is hidden

### 2. Auditability
- Complete audit trail
- Exportable for compliance
- Traceable to specific transactions

### 3. Interpretability
- Human-readable explanations
- Plain English summaries
- Step-by-step breakdowns

### 4. Accountability
- Analysts can verify decisions
- Compliance officers can audit
- Regulators can review

### 5. Fairness
- Bias mitigation is transparent
- Segment adjustments are documented
- FPR ratios are shown

---

## Closing Statement

**Say:**
> "You asked if the adaptive threshold is a black box. I've shown you:"
> 1. Complete audit trail of every decision
> 2. Human-readable explanations for each adjustment
> 3. Numerical documentation of all factors
> 4. Export functionality for compliance
> 5. Visual dashboard for easy review

> "This is the opposite of a black box. It's a glass box with complete transparency. Every decision is explainable, auditable, and accountable."

---

## Time Allocation

- Part 1 (Problem): 30 seconds
- Part 2 (Audit Trail): 1 minute
- Part 3 (Auditability): 1 minute
- Part 4 (Contrast): 30 seconds
- **Total: 3 minutes**

---

## Visual Cues to Emphasize

1. **Expandable cards** - Show the before/after of expanding a decision
2. **Color-coded badges** - Point out HIGH/MEDIUM/LOW sensitivity
3. **Numerical factors** - Highlight the exact adjustment values
4. **Export button** - Emphasize the audit trail can be saved
5. **Filter buttons** - Show you can focus on major decisions

---

## Success Criteria

Judge should understand:
- ✅ Every threshold adjustment has an explanation
- ✅ All factors are numerically documented
- ✅ Complete audit trail is maintained
- ✅ System is transparent and auditable
- ✅ This is NOT a black box
