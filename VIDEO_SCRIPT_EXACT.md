# 🎬 Exact Video Script - 4 Minutes

**Read this word-for-word. Time yourself. Practice once before recording.**

---

## [0:00 - 0:30] Opening & Problem (30 seconds)

*[Show: README on GitHub open in browser]*

**SAY EXACTLY:**

"Hi, I'm Vanshit Malik, and this is my FDE Data Foundations assignment.

The problem: NYC taxi fleet managers need to optimize vehicle allocation, but their data is fragmented across multiple systems. They can't track trip completion rates or operational efficiency.

I built an end-to-end data pipeline that consolidates NYC TLC data, validates it with business rules, models the trip workflow, and generates five operational metrics that directly support fleet allocation decisions."

---

## [0:30 - 2:45] Key FDE Judgment Call (2 minutes 15 seconds)

*[Show: src/validation/validators.py open, scroll to lines 105-125]*

**SAY EXACTLY:**

"The most important FDE judgment I made was how to handle zero-distance trips.

When I profiled the data, I found about three to five percent of trips showed zero distance but had positive fares and durations. I had three options:

Option one: Reject all zero-distance trips as invalid. But this would undercount revenue by two percent.

Option two: Accept all zero-distance trips. But this would include obvious data errors where both distance and fare are zero.

Option three: Apply a business rule. This is what I chose.

Here's the logic. A zero-distance trip is valid if... the duration is at least two minutes... AND... the fare is at least two fifty.

Why? Because NYC taxis charge for waiting time. If you're stuck in traffic or waiting at a red light, that's a legitimate charge even with zero movement.

If I rejected all zero-distance trips, we'd miss valid revenue. If I accepted all of them, we'd include data glitches.

This decision affects one hundred trips in our sample, about one percent. Fifty-three passed as valid waiting charges, forty-seven were rejected as data errors.

I documented this decision in three places: in the code with comments, in the config file with the threshold values, and in the README under assumptions."

---

## [2:45 - 3:30] Pipeline Execution (45 seconds)

*[Show: Terminal, run the pipeline]*

```bash
python src/pipeline/main_pipeline.py --reset-checkpoint
```

**SAY EXACTLY:**

"Let me run the complete pipeline.

It executes five phases: Ingest fetches data from NYC TLC. Validate applies our business rules and tracks why trips fail. Model builds the workflow with geographic and time enrichment. Metrics calculates our five KPIs. And Output generates the dashboard.

Notice the logging. Each validation failure is recorded with a specific reason. We track negative fares, time paradoxes, and those zero-distance trips. The pipeline checkpoints after each phase, so if something fails, we can resume without re-downloading data."

---

## [3:30 - 4:00] Results & Close (30 seconds)

*[Show: Dashboard in browser - data/output/dashboard_advanced_202401.html]*

**SAY EXACTLY:**

"Here are the results. Five operational metrics.

Trip completion rate: one hundred percent of valid trips passed validation.

Average trip duration: twenty minutes - our service baseline.

Revenue per mile: nineteen thirty-four - pricing effectiveness.

Peak hour utilization: eleven percent - this shows opportunity to shift more vehicles to peak times.

And geographic coverage: one hundred percent - excellent zone mapping.

These metrics directly support fleet allocation. Low peak utilization means managers should deploy more vehicles during rush hour.

The complete project is on GitHub with all source code, documentation, and this interactive dashboard. Thanks for watching."

---

## TIMING BREAKDOWN

- **0:00-0:30** = Problem (30 sec)
- **0:30-2:45** = FDE Judgment (2 min 15 sec)
- **2:45-3:30** = Pipeline Run (45 sec)  
- **3:30-4:00** = Results (30 sec)

**TOTAL: 4 minutes exactly**

---

## REHEARSAL TIPS

1. **Read it through once** to get familiar
2. **Time yourself** - should be 3:45 to 4:15
3. **Slow down** if you're under 3:30
4. **Practice transitions** between screens
5. **Don't ad-lib** - stick to the script

---

## SCREEN SEQUENCE

1. **GitHub README** (0:00-0:30)
2. **validators.py in editor** (0:30-2:45)
3. **Terminal** (2:45-3:30)
4. **Dashboard in browser** (3:30-4:00)

---

## IF YOU'RE RUNNING SHORT/LONG

**Too SHORT (under 3:30)?**
- Pause 2 seconds between sections
- Speak slower and more deliberately
- Add: "As you can see here..." when showing code

**Too LONG (over 4:30)?**
- Skip: "in our sample" phrases
- Cut: "I documented this in three places" - just say "documented"
- Trim: Just say metrics without the explanations

---

## FINAL CHECKLIST

- [ ] Script printed or on second screen
- [ ] All files open in tabs (README, validators.py, terminal, dashboard)
- [ ] Practiced once (timed at 3:45-4:15)
- [ ] Loom recording set to "Screen Only" or "Screen + Camera"
- [ ] Microphone tested
- [ ] Notifications turned off

**Now record! You've got this!** 🎬
