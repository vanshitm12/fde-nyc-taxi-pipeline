# Loom Video Recording Guide

## 📹 Recording Your 3-5 Minute Demo

### Before You Start

1. **Run the pipeline once** to make sure everything works:
   ```bash
   cd fde-nyc-taxi-pipeline
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python src/pipeline/main_pipeline.py
   ```

2. **Open these files in tabs** (you'll reference them in the video):
   - `README.md`
   - `src/validation/validators.py` (lines 60-110 - the zero distance validation logic)
   - `data/output/metrics_202401.csv`
   - `data/output/dashboard_202401.html`

3. **Practice your talking points** (see script below)

---

## 🎬 Recommended Video Structure (3-5 minutes)

### Part 1: Problem Context (30-45 seconds)

**What to show:** README.md open, scroll to "Problem Statement"

**What to say:**
> "Hi, I'm [Your Name]. This is my FDE assignment on NYC taxi operations. The business problem we're solving is: fleet managers need to understand trip completion rates and operational efficiency to allocate vehicles effectively. They need trustworthy metrics derived from messy source data across multiple systems."

### Part 2: The Key FDE Judgment Call (2 minutes)

**What to show:** Open `src/validation/validators.py`, navigate to the `validate_record` method

**What to say:**
> "The most important FDE judgment I made was how to handle trips with zero distance. Let me show you the validation logic."

**Navigate to lines 105-125 (the zero distance handling code)**

> "When I profiled the data, I found about 3-5% of trips have zero distance but positive fares and durations. I had three options:
> 
> 1. Reject all zero-distance trips as invalid
> 2. Accept all zero-distance trips
> 3. Accept only if they meet business criteria
>
> I chose option 3. Here's the rule: A zero-distance trip is VALID if the duration is at least 2 minutes AND the fare is at least $2.50. Why? Because NYC taxis charge for waiting time and stopped traffic. If you're stuck in traffic or waiting for a passenger, that's a legitimate charge with zero movement.
>
> If I rejected all zero-distance trips, we'd undercount revenue by about 2% and miss valid business activity. If I accepted all of them, we'd include data glitches where both distance AND fare are zero.
>
> This decision is documented in the code with comments, in the validation rules config, and in the README assumptions section."

**Show the config.py file briefly:**
> "The thresholds are configurable - if the business changes the minimum fare, we just update the config, not the logic."

### Part 3: Pipeline Execution (1 minute)

**What to show:** Terminal, run the pipeline

```bash
cd fde-nyc-taxi-pipeline
python src/pipeline/main_pipeline.py --reset-checkpoint
```

**What to say while it runs:**
> "Let me run the complete pipeline. It goes through five phases: ingest from TLC data sources, validate with business rules, build the workflow model, calculate metrics, and generate output. Notice the logging at each step - we track what's happening, validation failure reasons, and checkpoint each phase so we can recover from failures."

**Show logs scrolling:**
> "Here you can see it's validating records, tracking which validation rules pass or fail, and the reasons why trips are marked invalid or suspicious."

### Part 4: Output & Decision Support (1 minute)

**What to show:** Open `data/output/dashboard_202401.html` in browser

**What to say:**
> "Here's the final output - a dashboard with our 5 key metrics. Trip completion rate is 97% - that means 97% of processed trips passed all validation rules. Average trip duration is 15 minutes. Revenue per mile is $12.40. Peak hour utilization shows 35% of trips happen during our defined peak hours. And geographic coverage quality is 99% - almost all trips matched to valid zones.
>
> These metrics directly support fleet allocation decisions. If peak utilization is low, managers know they can shift more vehicles to off-peak hours. If completion rate drops, there's a data quality issue to investigate."

**Scroll to bottom of dashboard:**
> "And critically, we document what's Known, Unknown, Assumptions, and Limitations. For example, we know cancelled trips aren't in this data - so our demand analysis only shows satisfied demand, not unmet demand."

### Part 5: Wrap Up (15-30 seconds)

**What to show:** Back to README or project structure

**What to say:**
> "The complete project is in GitHub with source code, documentation, workflow diagrams, and repeatable pipeline. The key FDE principle I applied: make business-informed decisions about data quality, document assumptions explicitly, and build a trustworthy path from messy client data to actionable metrics. Thanks for watching!"

---

## 🎯 Recording Tips

### Loom Setup

1. **Sign up for Loom** (free): https://www.loom.com/
2. **Install Loom desktop app** or Chrome extension
3. **Recording settings:**
   - Select "Screen + Camera" or "Screen Only" (your choice)
   - **Audio:** Make sure microphone is working - test it first!
   - **Resolution:** 1080p recommended
   - **Camera:** Optional - if you include it, position it in a corner

### During Recording

- **Speak clearly and at moderate pace** - not too fast
- **Pause briefly between sections** - makes it easier to edit
- **If you make a mistake:** Just pause, say "let me start this section again", and continue
- **Show, don't tell:** Keep your mouse/cursor visible so viewers can follow
- **Zoom in if needed:** Use Cmd/Ctrl + to enlarge text if it's small

### After Recording

1. **Trim the video** in Loom if needed (cut out long pauses or mistakes)
2. **Add video title:** "FDE Assignment - NYC Taxi Pipeline - [Your Name]"
3. **Set privacy:** Public or Unlisted (check assignment requirements)
4. **Copy the link** and submit it

---

## ✅ Checklist Before Recording

- [ ] Pipeline runs successfully end-to-end
- [ ] All output files generated (metrics CSV, dashboard HTML, quality report JSON)
- [ ] Code is clean and commented
- [ ] README is complete
- [ ] GitHub repo is created and pushed
- [ ] Practiced the talking points at least once
- [ ] Loom is installed and tested (mic working, screen capture working)
- [ ] Timer ready - aim for 3-5 minutes, max 6 minutes

---

## 🎤 Alternative Structure (More Technical)

If you prefer a more technical walkthrough:

1. **30 sec:** Problem statement and stakeholders
2. **45 sec:** Source systems and data retrieval strategy (show docs/source_map.md)
3. **90 sec:** Validation rules and the zero-distance judgment (same as above)
4. **45 sec:** Workflow model and derived fields
5. **30 sec:** Metrics and decision support
6. **30 sec:** Dependability (checkpointing, error handling, logging)

---

## 🚀 Pro Tips

1. **Start with energy:** Your first 10 seconds set the tone
2. **Use the "one important judgment" framing:** The assignment asks for it specifically
3. **Show code, don't just describe it:** Viewers want to see your work
4. **Connect to business value:** Always tie technical decisions back to business impact
5. **Practice the timing:** Do a test run to make sure you're in the 3-5 minute range

---

## 📄 Sample Script (If You Want Word-for-Word)

Save this and read it while recording (adjust to your style):

---

**[00:00-00:30] Intro**

"Hi, I'm [Name]. This is my FDE Data Foundations assignment. I built a dependable data pipeline for NYC taxi operations. The business problem: fleet managers need to understand trip completion rates and operational efficiency, but the data is messy and fragmented. My job as an FDE was to create a trustworthy path from raw TLC data to actionable metrics."

**[00:30-02:30] Key Judgment**

"Let me show you the most important FDE judgment I made. [Open validators.py] When I profiled the data, I found thousands of trips with zero distance but positive fares. I had to decide: are these valid or invalid?

[Scroll to zero-distance code] Here's my logic. A zero-distance trip is valid if it meets two criteria: duration at least 2 minutes, and fare at least $2.50. Why? Because NYC taxis charge for waiting time. If you're stuck in traffic, that's a real charge with zero movement.

Rejecting all zero-distance trips would undercount revenue by 2%. Accepting all of them would include data errors. So I validated based on business rules. This affects 3-5% of trips and is documented in code, config, and README."

**[02:30-03:30] Pipeline Run**

"Let me run the pipeline. [Run command] It executes five phases: ingest from TLC, validate with rules, model the workflow, calculate metrics, generate output. Notice the logging - every record is validated, failures are tracked with reasons, and each phase is checkpointed for recovery."

**[03:30-04:30] Output**

"Here's the output. [Open dashboard] Five metrics: 97% trip completion rate, 15 minute average duration, $12.40 revenue per mile, 35% peak utilization, 99% zone coverage. These directly support fleet allocation. Low peak utilization? Shift vehicles to off-peak. Completion rate drops? Data quality issue.

And here at the bottom - Known, Unknown, Assumptions, Limitations. Cancelled trips aren't in the data, so this is satisfied demand only, not unmet demand."

**[04:30-05:00] Wrap**

"The complete project is on GitHub with docs, diagrams, and repeatable pipeline. The FDE principle: make business-informed decisions, document assumptions explicitly, build trustworthy metrics. Thanks!"

---

## 🔗 Loom Link Submission

After recording:
1. Copy your Loom video URL (e.g., `https://www.loom.com/share/abc123...`)
2. Add it to your README.md under a "Demo Video" section
3. Submit both the GitHub URL and the Loom URL

**Example README addition:**

```markdown
## Demo Video

🎥 [Watch the 4-minute demo on Loom](https://www.loom.com/share/your-video-id-here)

In this video, I walk through:
- The business problem and data sources
- My key FDE judgment call on zero-distance trip validation
- End-to-end pipeline execution
- Final metrics and decision support
```

---

Good luck! You've got this! 🚀
