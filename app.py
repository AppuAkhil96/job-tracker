# ─────────────────────────────────────────────────────────────────────────────
# APP.PY — Main Application File
#
# This is the entry point of the app. When you run "streamlit run app.py",
# Streamlit executes this file from top to bottom every time the user
# interacts with anything (clicks a button, types in a box, etc.).
# That's different from normal Python — there are no "event listeners".
# Streamlit just reruns the whole script and figures out what changed.
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# IMPORTS
# Think of imports like loading tools into your toolbox before you start work.
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st       # The main framework that turns Python into a web app
import pandas as pd          # Like Excel for Python — lets us work with tables of data
import plotly.express as px  # A charting library — creates bar charts, pie charts, line graphs etc.
from datetime import date    # Lets us work with today's date (used in the Add Application form)
import database as db        # Our own file (database.py) that handles saving/loading from SQLite


# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# This MUST be the very first Streamlit command in the file — before any other
# st. call. It sets the browser tab title, favicon icon, and layout width.
# "wide" makes the app stretch across the full screen width.
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Job Application Tracker",
    page_icon="💼",
    layout="wide"
)


# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS
# CSS controls how things *look* — colours, spacing, rounded corners etc.
# st.markdown() with unsafe_allow_html=True lets us inject raw HTML/CSS.
# Without this, we're limited to Streamlit's default styling only.
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    /* Makes the tab bar have a small gap between each tab */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }

    /* Gives each metric box (e.g. "Total Applications") a light grey card style */
    div[data-testid="metric-container"] {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# INITIALISE THE DATABASE
# Calls init_db() from database.py. This creates the SQLite file and table
# if they don't already exist. Safe to call on every page load —
# it uses "CREATE TABLE IF NOT EXISTS" so it never overwrites existing data.
# ─────────────────────────────────────────────────────────────────────────────

db.init_db()


# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# Defined once at the top so we can reuse them anywhere in the file.
# A Python list keeps order; a dict maps each status to a hex colour code.
# Hex colours are how CSS/web defines colours — #RRGGBB (red, green, blue).
# ─────────────────────────────────────────────────────────────────────────────

STATUS_OPTIONS = [
    "Applied", "Recruiter Call", "Interview",
    "Assessment", "Offer", "Rejected", "Withdrawn"
]

STATUS_COLOURS = {
    "Applied":        "#4A90E2",   # Blue
    "Recruiter Call": "#9B59B6",   # Purple
    "Interview":      "#F39C12",   # Orange
    "Assessment":     "#1ABC9C",   # Teal
    "Offer":          "#27AE60",   # Green
    "Rejected":       "#E74C3C",   # Red
    "Withdrawn":      "#95A5A6",   # Grey
}


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR NAVIGATION
# The sidebar is the panel on the left of the screen.
# st.sidebar.radio() creates clickable options — like a menu.
# The user's selection is stored in `page` as a string.
# The if/elif blocks below use this to decide which page to render.
# ─────────────────────────────────────────────────────────────────────────────

st.sidebar.title("💼 Job Tracker")
st.sidebar.markdown("Track every application in one place.")

# radio() = mutually exclusive options (you can only pick one at a time)
page = st.sidebar.radio("Navigate", ["📋 Applications", "➕ Add Application", "📊 Analytics"])


# =============================================================================
# PAGE 1: APPLICATIONS
#
# Shows all saved applications with:
#   - Filter by status (multiselect)
#   - Search by company/role (text input)
#   - Sort options (dropdown)
#   - Expandable cards for each application
#   - Update status & delete buttons per card
# =============================================================================

if page == "📋 Applications":
    st.title("📋 My Applications")

    # Fetch all applications from SQLite via our database module.
    # Returns a list of dicts — one dict per row in the database.
    apps = db.get_all_applications()

    # If nothing is in the database yet, show a hint and stop here.
    # The "else" block below only runs if there IS data.
    if not apps:
        st.info("No applications yet. Use **Add Application** to get started!")
    else:
        # Convert the list of dicts into a Pandas DataFrame.
        # A DataFrame is like an Excel table — rows are applications, columns are fields.
        # This lets us filter, sort, and search using simple Pandas syntax.
        df = pd.DataFrame(apps)

        # ── Filter & Search Controls ──────────────────────────────────────────
        # st.columns(3) splits the horizontal space into 3 equal sections.
        # "with col1:" means anything inside that block appears in column 1.
        col1, col2, col3 = st.columns(3)

        with col1:
            # multiselect = tick boxes for multiple choices.
            # default=STATUS_OPTIONS means all statuses are ticked by default.
            # Whatever the user ticks gets stored as a list in status_filter.
            status_filter = st.multiselect(
                "Filter by Status", STATUS_OPTIONS, default=STATUS_OPTIONS
            )

        with col2:
            # A plain text input box. Whatever the user types is stored in `search`.
            # Empty string "" if nothing is typed.
            search = st.text_input("Search by Company / Role")

        with col3:
            # selectbox = a single-choice dropdown.
            sort_by = st.selectbox("Sort by", [
                "Date Applied (Newest)", "Date Applied (Oldest)", "Company", "Status"
            ])

        # ── Apply Status Filter ───────────────────────────────────────────────
        # df[condition] keeps only the rows where the condition is True.
        # .isin(status_filter) checks if the value is in the selected list.
        # e.g. if status_filter = ["Applied", "Interview"], rows with "Rejected" are dropped.
        filtered = df[df["status"].isin(status_filter)]

        # ── Apply Search Filter ───────────────────────────────────────────────
        if search:
            # str.contains() checks if the search text appears in each cell.
            # case=False = ignore upper/lowercase ("deloitte" matches "Deloitte").
            # na=False = treat empty/null cells as non-matches (avoids errors).
            # | = OR operator — match if company OR role contains the search text.
            mask = (
                filtered["company"].str.contains(search, case=False, na=False) |
                filtered["role"].str.contains(search, case=False, na=False)
            )
            # Apply the mask — True rows are kept, False rows are dropped.
            filtered = filtered[mask]

        # ── Apply Sort ────────────────────────────────────────────────────────
        # A dict that maps the dropdown label to (column_name, ascending_bool).
        # True = ascending (A→Z, old→new), False = descending (Z→A, new→old).
        sort_map = {
            "Date Applied (Newest)": ("date_applied", True),
            "Date Applied (Oldest)": ("date_applied", False),
            "Company":               ("company", False),
            "Status":                ("status", False),
        }
        sort_col, sort_asc = sort_map[sort_by]   # Unpack the tuple for the chosen option
        filtered = filtered.sort_values(sort_col, ascending=sort_asc)

        # Show a count of how many applications are currently visible
        st.markdown(f"**{len(filtered)} application(s)** shown")

        # ── Render Application Cards ──────────────────────────────────────────
        # iterrows() loops through the DataFrame one row at a time.
        # _ is the row index (we don't need it, so we discard it with _).
        # `row` is a Series (like a dict) containing that row's values.
        for _, row in filtered.iterrows():

            # st.expander() = a collapsible section. The label is always visible;
            # clicking it reveals the full content inside.
            with st.expander(
                f"🏢 {row['company']}  —  {row['role']}  |  {row['status']}  |  {row['date_applied']}"
            ):
                # Two columns inside each card: left = platform/location/salary,
                # right = status/date/link
                col_a, col_b = st.columns(2)

                with col_a:
                    # row.get('field', '—') safely fetches a value.
                    # If the field is missing or None, it returns '—' instead of crashing.
                    st.markdown(f"**Platform:** {row.get('platform', '—')}")
                    st.markdown(f"**Location:** {row.get('location', '—')}")
                    st.markdown(f"**Salary:** {row.get('salary', '—')}")

                with col_b:
                    st.markdown(f"**Status:** {row['status']}")
                    st.markdown(f"**Date Applied:** {row['date_applied']}")
                    if row.get("job_url"):
                        # Only renders a clickable link if a URL was saved
                        st.markdown(f"[🔗 Job Listing]({row['job_url']})")

                if row.get("notes"):
                    st.markdown(f"**Notes:** {row['notes']}")

                # A horizontal divider line to visually separate info from action buttons
                st.divider()

                # Three columns for the action row: wide dropdown | narrow button | narrow button
                # [2, 1, 1] controls the relative widths — col1 is twice as wide as col2/col3
                upd_col1, upd_col2, upd_col3 = st.columns([2, 1, 1])

                with upd_col1:
                    # Dropdown pre-selected to this application's current status.
                    # index= sets which option is shown by default.
                    # STATUS_OPTIONS.index(row["status"]) finds the position of the current status
                    # in the list — e.g. "Interview" is at index 2.
                    #
                    # key= MUST be unique for every widget — Streamlit uses it to track
                    # which widget is which across reruns. Using the DB row ID guarantees uniqueness.
                    new_status = st.selectbox(
                        "Update Status",
                        STATUS_OPTIONS,
                        index=STATUS_OPTIONS.index(row["status"]),
                        key=f"status_{row['id']}"
                    )

                with upd_col2:
                    # st.button() returns True only in the moment it's clicked.
                    # The if block runs once, saves the change, then the page reruns.
                    if st.button("✅ Update", key=f"update_{row['id']}"):
                        db.update_status(row["id"], new_status)
                        st.success("Updated!")
                        st.rerun()  # Force a full page refresh so the new status appears immediately

                with upd_col3:
                    if st.button("🗑️ Delete", key=f"delete_{row['id']}"):
                        db.delete_application(row["id"])
                        st.warning("Deleted.")
                        st.rerun()  # Refresh so the deleted card disappears from the list


# =============================================================================
# PAGE 2: ADD APPLICATION
#
# A form with input fields for all job application details.
# Uses st.form() so the page only reruns on submit — not on every keystroke.
# Validates that company and role are filled in before saving.
# =============================================================================

elif page == "➕ Add Application":
    st.title("➕ Add New Application")

    # st.form() groups all inputs into one batch.
    # Streamlit normally reruns on every interaction (every keystroke, every click).
    # Wrapping in a form means: collect all inputs, then only rerun when "Submit" is clicked.
    # clear_on_submit=True resets all fields back to empty/default after a successful save.
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            company      = st.text_input("Company Name *")
            role         = st.text_input("Job Title / Role *")
            location     = st.text_input("Location")
            salary       = st.text_input("Salary Range (e.g. £35,000 – £45,000)")

        with col2:
            platform = st.selectbox("Platform Applied On", [
                "Reed", "Indeed", "LinkedIn", "CWJobs", "Glassdoor",
                "NHS Jobs", "TotalJobs", "Direct / Company Website", "Recruiter", "Other"
            ])
            status       = st.selectbox("Status", STATUS_OPTIONS)
            # date.today() gives today's date as the default value
            date_applied = st.date_input("Date Applied", value=date.today())
            job_url      = st.text_input("Job URL (optional)")

        # text_area = a multi-line text box (good for longer notes)
        notes = st.text_area("Notes (interview feedback, contact name, recruiter details, etc.)")

        # The actual submit button — nothing above gets processed until this is clicked.
        submitted = st.form_submit_button("💾 Save Application")

        if submitted:
            # Basic validation — we can't save without at least a company and role name.
            if not company or not role:
                st.error("Company and Role are required fields.")
            else:
                # str(date_applied) converts the Python date object into a text string
                # in "YYYY-MM-DD" format — e.g. "2026-04-14" — so SQLite can store it.
                db.add_application(
                    company=company,
                    role=role,
                    location=location,
                    salary=salary,
                    platform=platform,
                    status=status,
                    date_applied=str(date_applied),
                    job_url=job_url,
                    notes=notes
                )
                st.success(f"✅ Saved: **{role}** at **{company}**")


# =============================================================================
# PAGE 3: ANALYTICS
#
# Loads all application data and visualises it with:
#   - 5 summary metric cards (totals, response rate)
#   - Status breakdown donut chart
#   - Cumulative applications over time (line chart)
#   - Applications by platform (horizontal bar chart)
#   - Applications by week (vertical bar chart)
#   - Full data table with CSV export
# =============================================================================

elif page == "📊 Analytics":
    st.title("📊 Job Search Analytics")

    apps = db.get_all_applications()

    if not apps:
        st.info("Add some applications to see analytics!")
    else:
        df = pd.DataFrame(apps)

        # Convert the date column from plain text ("2026-04-14") to a proper
        # Pandas datetime object. This unlocks date-specific operations like
        # grouping by week, month, or extracting just the day name.
        df["date_applied"] = pd.to_datetime(df["date_applied"])

        # ── Summary Metrics ───────────────────────────────────────────────────
        # len(df) = total number of rows = total applications
        total = len(df)

        # Filter the DataFrame to matching rows, then count them with len().
        # .isin([...]) checks if the value is in the given list — useful for
        # grouping multiple statuses together.
        interviews = len(df[df["status"].isin(["Interview", "Assessment", "Offer"])])
        offers     = len(df[df["status"] == "Offer"])
        rejected   = len(df[df["status"] == "Rejected"])

        # "Responded" = anything beyond just "Applied" (i.e. they got back to us)
        responded     = len(df[df["status"] != "Applied"])

        # Calculate response rate as a percentage, rounded to nearest whole number.
        # The "if total else 0" prevents a division-by-zero error when there's no data.
        response_rate = round((responded / total) * 100) if total else 0

        # st.metric() displays a label + value in a clean card format.
        # 5 columns = 5 cards side by side across the top of the page.
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total Applications", total)
        c2.metric("Interviews / Assessments", interviews)
        c3.metric("Offers", offers)
        c4.metric("Rejected", rejected)
        c5.metric("Response Rate", f"{response_rate}%")

        st.divider()

        col_left, col_right = st.columns(2)

        # ── Chart 1: Status Donut Chart ───────────────────────────────────────
        with col_left:
            st.subheader("Status Breakdown")

            # value_counts() counts how many times each unique value appears in a column.
            # e.g. {"Applied": 12, "Interview": 3, "Rejected": 5}
            # reset_index() reshapes it from a Series into a 2-column DataFrame.
            status_counts = df["status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]  # Rename the columns to readable names

            # px.pie() = pie chart. hole=0.45 cuts a hole in the middle → donut shape.
            # color="Status" tells Plotly to colour each slice based on the Status column.
            # color_discrete_map= maps each status label to our pre-defined colour dict.
            fig_donut = px.pie(
                status_counts,
                names="Status",
                values="Count",
                hole=0.45,
                color="Status",
                color_discrete_map=STATUS_COLOURS
            )
            # Show both the percentage AND the label inside each slice of the donut.
            fig_donut.update_traces(textposition="inside", textinfo="percent+label")
            # Hide the separate legend (it's redundant since labels are already on the slices).
            # margin reduces whitespace around the chart.
            fig_donut.update_layout(showlegend=False, margin=dict(t=20, b=20))
            st.plotly_chart(fig_donut, use_container_width=True)

        # ── Chart 2: Cumulative Applications Over Time ────────────────────────
        with col_right:
            st.subheader("Cumulative Applications Over Time")

            # Group all applications by the date they were applied on, then count.
            # .dt.date strips the time component so we group by day only.
            # .size() counts the number of rows in each group.
            # .reset_index() turns the result into a clean 2-column DataFrame.
            timeline = df.groupby(df["date_applied"].dt.date).size().reset_index()
            timeline.columns = ["Date", "Applications"]

            # cumsum() = cumulative sum.
            # Instead of showing "3 applications on Monday, 2 on Tuesday",
            # it shows "3 total by Monday, 5 total by Tuesday, 10 total by Wednesday".
            # This gives a satisfying upward-trending line that shows your progress.
            timeline["Cumulative"] = timeline["Applications"].cumsum()

            fig_line = px.line(
                timeline,
                x="Date",
                y="Cumulative",
                labels={"Cumulative": "Total Applications"},
                markers=True,  # Adds a visible dot at each data point on the line
                color_discrete_sequence=["#4A90E2"]
            )
            fig_line.update_layout(margin=dict(t=20, b=20))
            st.plotly_chart(fig_line, use_container_width=True)

        st.divider()

        col_b1, col_b2 = st.columns(2)

        # ── Chart 3: Applications by Platform (Horizontal Bar) ────────────────
        with col_b1:
            st.subheader("Applications by Platform")

            platform_counts = df["platform"].value_counts().reset_index()
            platform_counts.columns = ["Platform", "Count"]

            # orientation="h" makes horizontal bars — better for reading long labels
            # like "Direct / Company Website" without them overlapping.
            fig_bar = px.bar(
                platform_counts,
                x="Count",
                y="Platform",
                orientation="h",
                color_discrete_sequence=["#9B59B6"]
            )
            # autorange="reversed" puts the most-used platform at the TOP of the chart
            # (by default Plotly puts the last item at the top for horizontal bars).
            fig_bar.update_layout(margin=dict(t=20, b=20), yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_bar, use_container_width=True)

        # ── Chart 4: Applications by Week (Vertical Bar) ─────────────────────
        with col_b2:
            st.subheader("Applications by Week")

            # dt.to_period("W") groups each date into its calendar week.
            # e.g. "2026-04-10" and "2026-04-14" both belong to the same week.
            # .apply(lambda r: r.start_time) converts each week period back to a
            # proper datetime (the Monday of that week) so Plotly can display it on an axis.
            # lambda is an anonymous (one-line) function — here it just calls .start_time on r.
            df["week"] = df["date_applied"].dt.to_period("W").apply(lambda r: r.start_time)

            weekly = df.groupby("week").size().reset_index()
            weekly.columns = ["Week Starting", "Applications"]

            fig_weekly = px.bar(
                weekly,
                x="Week Starting",
                y="Applications",
                color_discrete_sequence=["#27AE60"]
            )
            fig_weekly.update_layout(margin=dict(t=20, b=20))
            st.plotly_chart(fig_weekly, use_container_width=True)

        # ── Raw Data Table ────────────────────────────────────────────────────
        st.divider()
        st.subheader("All Applications")

        # Only display the user-facing columns (drop internal ones like 'id', 'created_at').
        display_cols = ["company", "role", "location", "platform", "status", "date_applied", "salary"]

        # st.dataframe() renders a scrollable, sortable table in the browser.
        # use_container_width=True makes it stretch to fill the available width.
        st.dataframe(
            df[display_cols].sort_values("date_applied", ascending=False),
            use_container_width=True
        )

        # ── CSV Export ────────────────────────────────────────────────────────
        # .to_csv(index=False) converts the DataFrame to a CSV-formatted string.
        # index=False stops it adding a row number column (0, 1, 2...) to the output.
        # .encode("utf-8") converts the string to bytes — required for file downloads.
        csv = df[display_cols].to_csv(index=False).encode("utf-8")

        # st.download_button() creates a button that triggers a browser file download.
        # The user gets a file called "job_applications.csv" with all their data.
        st.download_button(
            label="⬇️ Export to CSV",
            data=csv,
            file_name="job_applications.csv",
            mime="text/csv"
        )
