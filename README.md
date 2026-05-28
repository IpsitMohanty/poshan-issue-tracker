# Poshan Issue Tracker

Notebook-based issue-tracking workflow for **Poshan / governance operations**, built with Python, Pandas, and `ipywidgets`.

This repository provides a lightweight local system for logging, updating, validating, and filtering operational issues without needing a separate web app or database.

## What This Project Does

The project turns a Jupyter notebook into a small issue-management interface.

It supports:

- adding new issue records through interactive forms
- updating existing issues by issue ID
- storing issue data in a local CSV file
- auto-generating issue IDs in `STATE-YEAR-NUM` format
- classifying issues for validity and recency checks
- filtering recent issues by module and validity state

## Why It Exists

Operational issue lists are often maintained manually in spreadsheets, which makes them harder to validate consistently and update safely.

This notebook provides a more structured local workflow by combining:

- CSV-backed persistence
- basic business-rule validation
- guided form inputs
- issue status updates
- local filtering for review

It is especially useful when the team needs a simple internal tool rather than a full ticketing platform.

## Main Features

- `ipywidgets`-based add and update forms
- persistent CSV storage in `poshan_issue_store.csv`
- issue ID generation such as `OD-2026-001`
- automatic validity labeling for cases such as:
  - missing date
  - invalid date
  - outdated issue
  - closed issue without resolved date
- module and validity filters for quick review
- district, block, AWC code, severity, and assignment fields

## Repository Structure

- `Poshan_Issue_Log.ipynb`
  Main notebook containing the UI, storage logic, and validation rules.

- `poshan_issue_store.csv`
  Local issue data store created and updated by the notebook. This file is intentionally excluded from version control.

## How It Works

1. Open the notebook in Jupyter.
2. Run all cells.
3. Use the left-side form to add new issues.
4. Use the update form to modify status, assignment, remarks, or resolution details.
5. Review filtered issues by validity or module.
6. Persist changes back to the CSV store.

## Fields Captured

Typical issue records include:

- issue ID
- date reported
- district
- block
- AWC code
- module
- severity
- description
- status
- assigned to
- resolution / workaround
- date resolved
- remarks
- validity

## Running the Notebook

Install the main dependencies locally:

```bash
pip install pandas ipywidgets notebook
```

Then launch Jupyter and open the notebook:

```bash
jupyter notebook
```

## Current Scope

This is a lightweight local operational tool.

It does not currently include:

- multi-user authentication
- server-side APIs
- database storage
- workflow notifications
- audit logging beyond the CSV history you maintain locally
