# Submission checklist (GitHub via VS Code)

The assignment asks for the code **and the data** in a public GitHub repository, and the link
submitted in `raw.githubusercontent.com` format so it runs with `streamlit run <link>`.

## 1. Set your repository address in the script (before publishing)

Decide your repository name first (e.g. `electricity-dashboard`), then open `electricity_app.py`
and edit this line, near the top of the file:

```python
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/<USER>/<REPO>/main/"
```

Replace `<USER>` with your GitHub username and `<REPO>` with the repository name, e.g.

```python
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/myname/electricity-dashboard/main/"
```

Why: when Streamlit runs a script from a URL it downloads only the script, so the app reads the
two CSV files from this address.

## 2. Publish from VS Code

1. **File → Open Folder…** and open this folder.
2. Open the **Source Control** view (Ctrl/Cmd + Shift + G) → **Publish to GitHub**.
3. Sign in to GitHub if asked, enter the repository name from step 1 and choose
   **Publish to GitHub public repository** (it must be public).
4. When asked which files to include, keep all of them:
   - `electricity_app.py`
   - `Electricity_consumption_2015-2025.csv`
   - `Electricity_price_2015-2025.csv`
   - `requirements.txt`
   - `README.md`, `SUBMISSION.md`, `.gitignore`, `.gitattributes`
5. Check that the default branch is called **main** (shown in the bottom-left corner of VS Code).
   If it is `master`, use `master` instead of `main` in step 1 and in the link below.

## 3. Test the link

```bash
streamlit run https://raw.githubusercontent.com/<USER>/<REPO>/main/electricity_app.py
```

(with your real username and repository name; no `<` `>` characters). The app opens in the
browser and shows the figures for 2022-01-01 – 2024-06-01.

## 4. Submit in Moodle

Submit the link from step 3:

```
https://raw.githubusercontent.com/<USER>/<REPO>/main/electricity_app.py
```

Alternative: submit `electricity_app.py` as a file in Moodle (it uses the CSV files when they are
in the same folder as the script).

## Live app (optional extra)

The app is also deployed on Streamlit Community Cloud and opens directly in a browser:

https://electricity-dashboard-8xb7paadydr96th2e8o3v5.streamlit.app/

It redeploys automatically whenever changes are pushed to `main`. Submit it in Moodle next to
the raw link above, not instead of it.
