# Poshan Issue Tracker

A lightweight issue-tracking system for governance projects, built in Jupyter with:

- Persistent CSV storage
- Auto-validation of issue records
- Regex-based ID generation (STATE-YEAR-NUM)
- Validity classification (Outdated, Missing Date, Closed without Resolved Date, etc.)
- Interactive ipywidgets forms for adding, updating, and filtering issues

## Usage
1. Open Poshan_Issue_Log.ipynb in Jupyter.
2. Run all cells to load the interactive UI.
3. Add / Update issues with the forms.
4. Data is stored locally in poshan_issue_store.csv.

⚠️ The CSV file is excluded from version control so that live issue data stays private.
