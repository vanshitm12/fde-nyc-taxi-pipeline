# 🎥 Video Recording Guide for FDE Assignment

**This file is separate from the main repository documentation**

## Purpose
Create a 3-5 minute demonstration video explaining your FDE data pipeline project.

---

## Before Recording

### 1. Prepare Your Environment
```bash
cd fde-nyc-taxi-pipeline

# Ensure pipeline works
python src/pipeline/main_pipeline.py --reset-checkpoint

# Open these files in tabs:
- README.md
- src/validation/validators.py (lines 105-125)
- data/output/dashboard_advanced_202401.html
```

### 2. Setup Loom
1. Sign up: https://www.loom.com (free account)
2. Install Loom desktop app or Chrome extension
3. Test recording: Screen + Camera (or Screen Only)
4. Check microphone works

---

## Video Structure (3-5 minutes)

### Part 1: Problem Context (30-45 seconds)
**Show:** README.md open, scroll to "Problem Statement"

**Script:**
```
"Hi, I'm Vanshit Malik. This is my FDE assignment on NYC taxi operations. 

The business problem: Fleet managers need to understand trip completion rates 
and operational efficiency to allocate vehicles effectively. They need trustworthy 
metrics from messy source data across multiple systems.

This pipeline solves that by consolidating TLC data, implementing business-informed 
validation, modeling the trip workflow, and generating 5 operational metrics."
```

---

### Part 2: Key FDE Judgment (2 minutes)
**Show:** `src/validation/validators.py` (lines 105-125)

**Script:**
```
"The most important FDE judgment I made was handling zero-distance trips.

When profiling the data, I found 3-5% of trips have zero distance but positive 
fares and durations. I had three options:

1. Reject all as invalid - would undercount revenue by 2%
2. Accept all - would include data errors  
3. Apply business rules - my choice

Here's the logic: A zero-distance trip is valid if duration ≥ 2 minutes AND 
fare ≥ $2.50. Why? NYC taxis charge for waiting time and stopped traffic.

If you're stuck in traffic, that's a real charge with zero movement. This is 
documented in code, config, and the README assumptions section."
```

**Show the code:**
```python
if distance == 0:
    if duration_minutes >= 2 and fare >= 2.50:
        # Valid waiting time charge
        return STATUS_VALID
    else:
        # Data error
        return STATUS_INVALID
```

---

### Part 3: Pipeline Execution (1 minute)
**Show:** Terminal

**Run:**
```bash
python src/pipeline/main_pipeline.py --reset-checkpoint
```

**Script:**
```
"Let me run the complete pipeline. It executes 5 phases:

1. Ingest - fetch from TLC sources
2. Validate - apply business rules  
3. Model - build workflow entities
4. Metrics - calculate KPIs
5. Output - generate dashboard

Notice the logging at each step. We track validation failures with specific 
reasons, and checkpoint each phase for recovery."
```

---

### Part 4: Dashboard & Results (1 minute)
**Show:** `data/output/dashboard_advanced_202401.html` in browser

**Script:**
```
"Here's the output dashboard with our 5 key metrics:

• Trip Completion Rate: 100% - all valid trips passed validation
• Average Trip Duration: 20.1 minutes - service efficiency baseline
• Revenue per Mile: $19.34 - pricing effectiveness
• Peak Hour Utilization: 11.5% - shows opportunity for fleet reallocation
• Geographic Coverage: 100% - excellent zone mapping

These metrics directly support fleet allocation decisions. If peak utilization 
is low, managers can shift vehicles to off-peak hours. If completion rate drops, 
there's a data quality issue to investigate.

Critically, we document what's Known, Unknown, Assumptions, and Limitations. 
For example, cancelled trips aren't in this data - so demand analysis only 
shows satisfied demand, not unmet demand."
```

---

### Part 5: Wrap Up (30 seconds)
**Show:** README or repository page

**Script:**
```
"The complete project is on GitHub with source code, documentation, workflow 
diagrams, and a repeatable pipeline.

The key FDE principle I applied: make business-informed decisions about data 
quality, document assumptions explicitly, and build a trustworthy path from 
messy client data to actionable metrics.

Thanks for watching!"
```

---

## Recording Tips

### Before You Start
- ✅ Close unnecessary tabs/windows
- ✅ Turn off notifications
- ✅ Check microphone levels
- ✅ Practice once through
- ✅ Have water nearby

### During Recording
- 🎤 Speak clearly at moderate pace
- 🖱️ Keep cursor visible for viewers to follow
- ⏸️ Pause between sections (easier to edit)
- 🔄 If you mess up, pause and restart that section
- 📏 Use Cmd/Ctrl + to zoom if text is small

### After Recording
1. Trim video in Loom editor (cut long pauses)
2. Add title: "FDE Assignment - NYC Taxi Pipeline - Vanshit Malik"
3. Set to Public or Unlisted
4. Copy share link
5. Submit

---

## Sample Timing Breakdown

```
0:00-0:30   Problem statement & context
0:30-2:30   Zero-distance validation judgment (THE KEY PART)
2:30-3:30   Pipeline execution  
3:30-4:30   Dashboard & metrics
4:30-5:00   Wrap up
```

Total: 3-5 minutes

---

## Common Mistakes to Avoid

❌ **Don't:** Read code line-by-line  
✅ **Do:** Explain the logic and why it matters

❌ **Don't:** Rush through  
✅ **Do:** Speak at normal conversational pace

❌ **Don't:** Apologize or say "I should have..."  
✅ **Do:** Be confident - your work is excellent

❌ **Don't:** Go over 6 minutes  
✅ **Do:** Keep it tight and focused

❌ **Don't:** Just narrate what's on screen  
✅ **Do:** Explain WHY each decision was made

---

## Key Points to Hit

1. **Business Problem**: Fleet allocation, data quality
2. **Your Judgment**: Zero-distance validation (THE MOST IMPORTANT)
3. **Business Rationale**: Waiting charges are valid
4. **Implementation**: Show the actual code
5. **Impact**: 3-5% of trips, 2% revenue impact
6. **Documentation**: Assumptions recorded
7. **Output**: 5 metrics supporting decisions
8. **Known Limitations**: Documented explicitly

---

## Submission

After recording:
1. Get your Loom share link
2. Submit alongside GitHub repository URL
3. No need to add the link to README

**Your Repository:**
https://github.com/vanshitm12/fde-nyc-taxi-pipeline

**Your Video:**
[Your Loom link here]

---

## Quick Reference Commands

```bash
# View dashboard
open data/output/dashboard_advanced_202401.html

# Run pipeline
python src/pipeline/main_pipeline.py --reset-checkpoint

# View validation code
open src/validation/validators.py
# Navigate to lines 105-125
```

---

## Final Checklist

- [ ] Loom account created
- [ ] Pipeline runs successfully
- [ ] Dashboard opens properly
- [ ] Practiced talking points once
- [ ] Microphone tested
- [ ] 3-5 minute target time
- [ ] Explained zero-distance judgment clearly
- [ ] Showed actual code
- [ ] Demonstrated dashboard
- [ ] Stayed under 6 minutes

---

**Good luck! You've built something impressive - show it off!** 🚀
