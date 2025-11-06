# 🧭 PRD — 2-Week Staffing Suggester (Full Stack Interactive Tool)

**Owner:** Hasti Hosseinizand  
**Version:** v2.1  
**Primary Agent:** Roo Code  
**Frameworks:** Python 3.11, pandas, Streamlit  
**Goal:** Build an interactive staffing tool where the CEO and PMs can edit inputs directly, then generate and view proposed staffing within the same table.

---

## 1️⃣ Overview & Goal

### Purpose
Create an **interactive Streamlit app** that allows:
- The **CEO** to fill in the **mandatory** project details for upcoming work.  
- The **Project Managers** to maintain the **resourcing view** of current people.  
- The tool to automatically generate a **proposed staffing plan for the next two weeks**, appended to the same Prospective Projects table.

### Vision
In one shared web page:
1. Two editable tables are shown — *Prospective Projects* and *Resourcing View*.  
2. CEO/PMs can edit cells inline (add rows, toggle Yes/No).  
3. When “Run Staffing Suggestion” is clicked:  
   - The backend computes assignments.  
   - The **Prospective Projects** table updates in-place with four new “Proposed” columns.  
4. The combined table can be downloaded as a CSV.

---

## 2️⃣ Inputs (Editable Tables)

### Input 1 — Prospective_Projects
Editable by: **CEO** (mandatory fields) and **PMs** (optional staffing fields).

**Columns and Rules**

| Column | Required For | Editable By | Type / Values | Description |
|---------|---------------|--------------|----------------|--------------|
| **Project** | CEO ✅ | CEO | string | Unique project name |
| **UseCase** | CEO ✅ | CEO | string | Project use case (e.g., Forecasting, Optimization) |
| **Starts_Week1** | CEO ✅ | CEO | Yes/No | Indicates if project starts next week |
| **Starts_Week2** | CEO ✅ | CEO | Yes/No | Indicates if project starts the following week |
| **Week1_DS_Needed** | Optional | CEO or PM | int ≥ 0 | Number of Data Scientists needed in week 1 |
| **Week1_DE_Needed** | Optional | CEO or PM | int ≥ 0 | Number of Data Engineers needed in week 1 |
| **Week2_DS_Needed** | Optional | CEO or PM | int ≥ 0 | Number of Data Scientists needed in week 2 |
| **Week2_DE_Needed** | Optional | CEO or PM | int ≥ 0 | Number of Data Engineers needed in week 2 |

**Validation**
- First 4 columns are mandatory and must be non-empty.  
- Optional numeric columns default to 0 if blank.  
- “Yes/No” normalized to booleans internally.  
- Duplicate project names → error.

---

### Input 2 — Resourcing_View
Editable by: **Project Managers**

| Column | Type / Values | Description | Validation |
|---------|----------------|--------------|-------------|
| Project | string | Current project the person belongs to | optional context |
| ResourceName | string | Person’s name (unique) | required |
| Role | DS or DE | Data Scientist / Engineer | required |
| Week1_Occupied | Yes/No | Whether occupied in week 1 | required |
| Week2_Occupied | Yes/No | Whether occupied in week 2 | required |

Derived:  
- `Available_Week1 = (Week1_Occupied == No)`  
- `Available_Week2 = (Week2_Occupied == No)`

---

## 3️⃣ Output (Extended Prospective Projects Table)

The output **extends the same Prospective_Projects table** with four additional columns:

| Column | Type | Description |
|---------|------|-------------|
| Proposed_DS_Week1 | string | Comma-separated Data Scientists assigned in week 1 |
| Proposed_DS_Week2 | string | Comma-separated Data Scientists assigned in week 2 |
| Proposed_DE_Week1 | string | Comma-separated Data Engineers assigned in week 1 |
| Proposed_DE_Week2 | string | Comma-separated Data Engineers assigned in week 2 |

After running, users see the same editable table updated with these new columns and can download it via a **“Download Staffing Plan”** button.

---

## 4️⃣ Core Algorithm (Backend Logic)

**Objective:** Assign available resources to open project needs for Weeks 1 and 2.

**Assumptions**
1. A person can work on only one project per week.  
2. If assigned in Week 1, keep them in Week 2 if still available.  
3. Role match required (DS→DS, DE→DE).  
4. Planning horizon: 2 weeks only.  
5. Deterministic alphabetical tie-break.

**Steps**
1. Normalize and validate both inputs.  
2. Build availability lists for DS/DE by week.  
3. For each project in order:  
   - **Week 1:**  
     - If Starts_Week1 = True, assign available DS and DE until needs met.  
   - **Week 2:**  
     - Prefer Week 1 assignees if still free; otherwise pick new people.  
   - Mark assigned resources as unavailable for those weeks.  
4. Append names to corresponding “Proposed” columns.  
5. Record shortages (e.g., missing roles) in `/output/assignment_log.md`.

---

## 5️⃣ Frontend (Streamlit UI)

**Framework:** Streamlit 1.36+  
**Purpose:** Enable in-browser editing, generation, and download.

### Layout
```
🎢 2-Week Staffing Suggester

[TAB 1] Prospective Projects
  • Editable table (st.data_editor)
  • Mandatory columns shown first (Project, UseCase, Starts_Week1, Starts_Week2)
  • Optional columns (Week1_DS/DE_Needed, Week2_DS/DE_Needed)
  • 'Run Staffing Suggestion' button updates the same table inline

[TAB 2] Resourcing View
  • Editable table for PMs
  • Displays resource name, role, and week-wise occupancy

[Output]
  • Same Prospective Projects table extended with 'Proposed_*' columns
  • 'Download Staffing Plan' button
```

### Streamlit Components
| Component | Function |
|------------|-----------|
| `st.data_editor()` | Interactive editing for both tables |
| `st.tabs()` | Switch between CEO and PM tables |
| `st.button("Run Staffing Suggestion")` | Trigger backend logic |
| `st.dataframe()` | Display updated table with proposed assignments |
| `st.download_button()` | Export combined table as CSV |
| `st.toast()` / `st.warning()` | User feedback for missing mandatory fields |

### Frontend Dependencies
- `streamlit`
- `pandas`
- `io`
- Local import: `scripts.assigner`

---

## 6️⃣ CLI Mode (Optional)
```bash
python main.py \
  --pros data/Prospective_Projects.csv \
  --res  data/Resourcing_View.csv \
  --out  output/Proposed_Staffing.csv
```

---

## 7️⃣ File Structure
```
/docs/
  prd_fullstack_v2.md
/scripts/
  io_utils.py
  assigner.py
  formatter.py
  logger.py
main.py
app.py                # Streamlit frontend
/data/
  Prospective_Projects.csv
  Resourcing_View.csv
/output/
  Proposed_Staffing.csv
  assignment_log.md
requirements.txt
README.md
```

---

## 8️⃣ Success Criteria
| Area | Target |
|------|---------|
| Functionality | One person per project/week; continuity across weeks |
| Usability | CEO/PMs can edit directly; clear required vs optional fields |
| Output | Proposed columns appear in same table |
| Performance | < 2 s on small CSVs |
| Reliability | Deterministic, repeatable results |
| Integration | Runs in GitPod or local Streamlit session |

---

## 9️⃣ Edge Cases
- All resources occupied → empty “Proposed” columns.  
- Project starts in Week 2 only → skip Week 1.  
- Missing optional fields → treated as 0.  
- Invalid Yes/No → coerced and warned.  
- Duplicates in project or person names → raise error.

---

## 🔠 Future Enhancements
| Theme | Idea |
|--------|------|
| Optimization | OR-Tools for global optimal matching |
| Cloud Storage | Sync editable tables with Google Sheets |
| Access Control | Separate CEO vs PM edit rights |
| Notifications | Slack or email summary |
| History | Weekly snapshots of staffing output |
| Visualization | Charts for utilization and shortages |

---

## 1️⃣1️⃣ Technical Setup
**Backend Dependencies**
```
pandas==2.2.1
```

**Frontend Dependencies**
```
streamlit==1.36.0
```

**Run Commands**
```bash
# Backend
python main.py --pros data/Prospective_Projects.csv --res data/Resourcing_View.csv

# Frontend
streamlit run app.py
```

**Environment**
- No external DB or API.  
- Runs fully offline.  
- Works in GitPod, Codespaces, or local VS Code.

---

## 1️⃣2️⃣ Implementation Plan
| Phase | Task | Deliverable |
|--------|------|-------------|
| 1 | Backend scaffolding (`assigner`, `io_utils`) | Working CLI algorithm |
| 2 | Streamlit UI with editable tables | CEO & PM editing working |
| 3 | Integrate backend with UI button | Single unified workflow |
| 4 | Add validations, required/optional field highlighting | UX clarity |
| 5 | Final polish & demo CSV export | Hackathon demo-ready |

---

**End of PRD — v2.1 Full-Stack Interactive Staffing Tool**

