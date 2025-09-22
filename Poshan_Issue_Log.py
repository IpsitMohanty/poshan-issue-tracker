#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os, re
import pandas as pd
from datetime import datetime, date
import ipywidgets as widgets
from IPython.display import display, clear_output

# -----------------------
# CSV storage setup
# -----------------------
STORE_CSV = "poshan_issue_store.csv"

COLUMNS = [
    "Issue ID","Date Reported","District","Block","AWC Code",
    "Module","Severity","Description","Status",
    "Assigned To","Resolution / Workaround","Date Resolved","Remarks","Validity"
]

ISSUE_ID_RE = re.compile(r"^(?P<state>[A-Z]{2})-(?P<year>\d{4})-(?P<num>\d{3})$")

def _ensure_store():
    """Ensure CSV exists with proper columns"""
    if not os.path.exists(STORE_CSV):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(STORE_CSV, index=False)
    df = pd.read_csv(STORE_CSV)
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""
    return df[COLUMNS]

def _save_store(df: pd.DataFrame):
    df = classify_issue(df)   # 🔹 always re-check before saving
    df.to_csv(STORE_CSV, index=False)

def _to_date(x):
    if pd.isna(x) or x in ["", None]:
        return ""
    try:
        return pd.to_datetime(x).strftime("%d-%b-%Y")
    except:
        return str(x)

# -----------------------
# Validity classification
# -----------------------
def classify_issue(df):
    df = df.copy()
    today = pd.to_datetime(date.today())
    validity = []
    for _, row in df.iterrows():
        val = row.get("Validity","").strip()  # 🔹 keep manual value if present
        if not val:  # only auto-compute when blank
            dr = row.get("Date Reported","").strip()
            ds = row.get("Status","")
            resolved = row.get("Date Resolved","").strip()
            try:
                if not dr:
                    val = "Missing Date"
                else:
                    d = pd.to_datetime(dr, errors="coerce")
                    if pd.isna(d):
                        val = "Invalid Date"
                    elif (today - d).days > 180:
                        val = "Outdated"
                if ds == "Closed" and not resolved:
                    val = "Closed w/o Resolved Date"
            except:
                val = "Invalid Date"
        validity.append(val)
    df["Validity"] = validity
    return df

def load_data():
    df = _ensure_store()
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""
        else:
            df[col] = df[col].astype(str).fillna("")
    return classify_issue(df[COLUMNS])

def get_next_issue_id(df, state_code="OD"):
    year = datetime.now().year
    mask = df["Issue ID"].astype(str).str.match(ISSUE_ID_RE)
    current_year = df[mask & df["Issue ID"].astype(str).str.contains(f"-{year}-")]
    if current_year.empty:
        next_num = 1
    else:
        nums = [
            int(m.group("num"))
            for x in current_year["Issue ID"].astype(str)
            if (m := ISSUE_ID_RE.match(str(x)))
        ]
        next_num = (max(nums)+1) if nums else 1
    return f"{state_code}-{year}-{next_num:03d}"

def add_issue(df, record: dict):
    rec = {col: record.get(col, "") for col in COLUMNS}
    if not rec["Issue ID"]:
        rec["Issue ID"] = get_next_issue_id(df)
    df = pd.concat([df, pd.DataFrame([rec])], ignore_index=True)
    return classify_issue(df)

def update_issue(df, issue_id, updates: dict):
    mask = df["Issue ID"].astype(str) == str(issue_id)
    if not mask.any():
        raise ValueError(f"Issue ID not found: {issue_id}")
    for k, v in updates.items():
        if k in df.columns:
            if "Date" in k:
                v = _to_date(v)
            df.loc[mask, k] = str(v) if v is not None else ""
    return classify_issue(df)

# -----------------------
# District & Module options
# -----------------------
districts = [
    "","Angul","Balangir","Balasore","Bargarh","Bhadrak","Boudh","Cuttack",
    "Deogarh","Dhenkanal","Gajapati","Ganjam","Jagatsinghpur","Jajpur","Jharsuguda",
    "Kalahandi","Kandhamal","Kendrapara","Keonjhar","Khordha","Koraput","Malkangiri",
    "Mayurbhanj","Nabarangpur","Nayagarh","Nuapada","Puri","Rayagada","Sambalpur",
    "Sonepur","Sundargarh"
]

modules = [
   "", "SNP (Nutrition)",
    "Beneficiary Registration",
    "Growth Monitoring",
    "APAAR (Education ID)",
    "Home Visits",
    "Dashboard (UI / Reports)",
    "eKYC / FRS",
    "App Functionality",
    "Backend / API (Infra, DevOps)",
    "Other"
]

# -----------------------
# Shared Issue Dropdown
# -----------------------
df = load_data()
issue_dropdown = widgets.Dropdown(
    description="Issue ID",
    options=list(df["Issue ID"].dropna().unique())
)

# -----------------------
# Add Issue Form
# -----------------------
date_reported = widgets.DatePicker(
    description="Date Reported",
    disabled=False
)

district = widgets.Dropdown(description="District", options=districts)
block = widgets.Text(description="Block")
awc = widgets.Text(description="AWC Code")
module = widgets.Dropdown(description="Module", options=modules)
severity = widgets.Dropdown(description="Severity", options=["","High","Medium","Low"])
desc = widgets.Textarea(description="Issue", placeholder="Describe the issue")

output_add = widgets.Output()
button_add = widgets.Button(description="Add Issue", button_style="success")

def on_add_click(b):
    with output_add:
        clear_output()
        df = load_data()
        record = {
            "Date Reported": _to_date(date_reported.value) if date_reported.value else "",
            "District": district.value,
            "Block": block.value,
            "AWC Code": awc.value,
            "Module": module.value,
            "Severity": severity.value,
            "Description": desc.value,
            "Status": "Open"
        }
        df = add_issue(df, record)
        _save_store(df)
        issue_dropdown.options = list(df["Issue ID"].dropna().unique())
        print("✅ Issue saved!")

button_add.on_click(on_add_click)

add_form = widgets.VBox([date_reported, district, block, awc, module, severity, desc, button_add, output_add])

# -----------------------
# Update Issue Form (with DatePicker & Validity dropdown)
# -----------------------
status_dropdown = widgets.Dropdown(description="Status", options=["Open","In Progress","Closed"])
date_reported_update = widgets.DatePicker(description="Date Reported")  # 🔹 new
validity_update = widgets.Dropdown(
    description="Validity",
    options=["","Valid","Missing Date","Outdated","Closed w/o Resolved Date","Invalid Date"]
)
district_update = widgets.Dropdown(description="District", options=districts)
block_update = widgets.Text(description="Block")
awc_update = widgets.Text(description="AWC Code")
module_update = widgets.Dropdown(description="Module", options=modules)
severity_update = widgets.Dropdown(description="Severity", options=["","High","Medium","Low"])
desc_update = widgets.Textarea(description="Description")
assigned_to = widgets.Text(description="Assigned To")
resolution = widgets.Textarea(description="Resolution")
remarks = widgets.Textarea(description="Remarks")

output_update = widgets.Output()
button_update = widgets.Button(description="Update Issue", button_style="info")

def on_update_click(b):
    with output_update:
        clear_output()
        issue_id = issue_dropdown.value
        if not issue_id:
            print("⚠️ Select an Issue ID first.")
            return

        df = load_data()
        current_row = df[df["Issue ID"] == issue_id].iloc[0]

        updates = {
            "Status": status_dropdown.value or current_row["Status"],
            "Date Reported": _to_date(date_reported_update.value) if date_reported_update.value else current_row.get("Date Reported", ""),
            "Validity": validity_update.value or current_row.get("Validity",""),
            "District": district_update.value or current_row["District"],
            "Block": block_update.value or current_row["Block"],
            "AWC Code": awc_update.value or current_row["AWC Code"],
            "Module": module_update.value or current_row["Module"],
            "Severity": severity_update.value or current_row["Severity"],
            "Description": desc_update.value if desc_update.value.strip() else current_row["Description"],
            "Assigned To": assigned_to.value if assigned_to.value.strip() else current_row.get("Assigned To", ""),
            "Resolution / Workaround": resolution.value if resolution.value.strip() else current_row.get("Resolution / Workaround", ""),
            "Remarks": remarks.value if remarks.value.strip() else current_row.get("Remarks", "")
        }

        if status_dropdown.value == "Closed":
            updates["Date Resolved"] = _to_date(date.today())
        else:
            updates["Date Resolved"] = current_row.get("Date Resolved", "")

        df2 = update_issue(df, issue_id, updates)
        _save_store(df2)

        df3 = load_data()
        print(f"✅ Issue {issue_id} updated")
        display(df3[df3["Issue ID"] == issue_id])

button_update.on_click(on_update_click)

def on_issue_select(change):
    if change["new"]:
        df = load_data()
        current_row = df[df["Issue ID"] == change["new"]].iloc[0]
        status_dropdown.value = current_row.get("Status", "Open")
        validity_update.value = current_row.get("Validity", "")
        # set Date Reported in update form
        date_val = current_row.get("Date Reported", "")
        try:
            date_reported_update.value = pd.to_datetime(date_val) if date_val else None
        except:
            date_reported_update.value = None
        district_update.value = current_row.get("District", "") if current_row.get("District", "") in districts else ""
        block_update.value = current_row.get("Block", "")
        awc_update.value = current_row.get("AWC Code", "")
        module_update.value = current_row.get("Module", "Other") if current_row.get("Module", "Other") in modules else "Other"
        severity_update.value = current_row.get("Severity", "Medium") if current_row.get("Severity", "Medium") in ["High","Medium","Low"] else "Medium"
        desc_update.value = current_row.get("Description", "")
        assigned_to.value = current_row.get("Assigned To", "")
        resolution.value = current_row.get("Resolution / Workaround", "")
        remarks.value = current_row.get("Remarks", "")

issue_dropdown.observe(on_issue_select, names="value")

update_form = widgets.VBox([
    issue_dropdown, status_dropdown, date_reported_update, validity_update,
    district_update, block_update, awc_update,
    module_update, severity_update, desc_update,
    assigned_to, resolution, remarks,
    button_update, output_update
])

# -----------------------
# Validity & Module Filters
# -----------------------
validity_filter = widgets.Dropdown(
    description="Validity",
    options=["All","Valid","Missing Date","Outdated","Closed w/o Resolved Date","Invalid Date"],
    value="All"
)

module_filter = widgets.Dropdown(
    description="Module",
    options=["All"] + modules,
    value="All"
)

output_filter = widgets.Output()

def apply_filters(*args):
    with output_filter:
        clear_output()
        df = load_data()

        # Apply validity filter
        if validity_filter.value != "All":
            df = df[df["Validity"] == validity_filter.value]

        # Apply module filter
        if module_filter.value != "All":
            df = df[df["Module"] == module_filter.value]

        display(df.tail(10))

validity_filter.observe(apply_filters, names="value")
module_filter.observe(apply_filters, names="value")

# -----------------------
# Display forms + filters
# -----------------------
display(widgets.VBox([
    widgets.HBox([add_form, update_form]),
    widgets.HBox([validity_filter, module_filter]),
    output_filter 
]))


# In[2]:





# In[ ]:




