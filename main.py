import streamlit as st
import pandas as pd

# ---------- Reset Callback Functions ----------
def reset_college():
    st.session_state["college_query"] = ""

def reset_code():
    st.session_state["college_code_query"] = ""

def reset_category():
    st.session_state["category_query"] = "GM"

def reset_course():
    st.session_state["course_query"] = ""

# ---------- Utility Functions ----------
def normalize(text):
    return ''.join(text.lower().split()).replace('.', '') if isinstance(text, str) else ''

def match_college_name(input_text, all_colleges):
    norm_input = normalize(input_text)
    return [c for c in all_colleges if normalize(c).startswith(norm_input)]

# ---------- Data Loading ----------
@st.cache_data
def load_data(path='kcet_cutoffs.csv'):
    df = pd.read_csv(path)
    df['Cut-Off Rank'] = pd.to_numeric(df['Cut-Off Rank'], errors='coerce')
    df.dropna(subset=['Cut-Off Rank'], inplace=True)
    for col in ['College Code', 'College Name', 'Category', 'Course Name']:
        df[col] = df[col].astype(str)
    return df

df = load_data()

# ---------- Page Config ----------
st.set_page_config(page_title="KCET College Recommender", layout="wide")
st.title("KCET Cut-Off Rank Latest")
st.markdown("""
Enter your **KCET rank**, then refine results using the filters below.
""", unsafe_allow_html=True)

# ---------- Main Rank Input ----------
# input_row = st.columns([0.5])
# with input_row[0]:
#     rank = st.number_input("Enter your KCET Rank:", min_value=1, step=1, format="%d")

# ---------- Apply Rank Filter ----------
filtered = df.copy()
# filtered = filtered[filtered['Cut-Off Rank'] >= rank]

# ---------- Column-Level Filters ----------
st.markdown("### Filter Results")
filter_cols = st.columns(5)
with filter_cols[0]:
    filter_code = st.text_input("College Code Filter").strip().lower()
with filter_cols[1]:
    filter_name = st.text_input("College Name Filter").strip().lower()
with filter_cols[2]:
    filter_category = st.selectbox("Category Filter", [""] + sorted(filtered['Category'].unique()), index=([""] + sorted(filtered['Category'].unique())).index("GM") if "GM" in filtered['Category'].unique() else 0)
with filter_cols[3]:
    filter_course = st.text_input("Course Name Filter").strip().lower()
with filter_cols[4]:
    filter_rank = st.number_input("Cutoff Rank ≤", min_value=0, step=1)

# Apply column filters
if filter_code:
    filtered = filtered[filtered['College Code'].str.lower().str.contains(filter_code)]
if filter_name:
    filtered = filtered[filtered['College Name'].str.lower().str.contains(filter_name)]
if filter_category:
    filtered = filtered[filtered['Category'] == filter_category]
if filter_course:
    filtered = filtered[filtered['Course Name'].str.lower().str.contains(filter_course)]
if filter_rank > 0:
    filtered = filtered[filtered['Cut-Off Rank'] >= filter_rank]

filtered = filtered.sort_values(by='Cut-Off Rank')

# ---------- Display Results ----------
if filtered.empty:
    st.warning("No colleges found matching your criteria.")
else:
    st.subheader(f"Recommended Colleges")
    st.dataframe(
        filtered[['College Code', 'College Name', 'Category', 'Course Name', 'Cut-Off Rank']],
        use_container_width=True,
        hide_index=True
    )
    csv = filtered.to_csv(index=False)
    st.download_button("Download CSV", csv, f"kcet_rank_recommendations.csv", "text/csv")

# ---------- Disclaimer ----------
st.markdown("---")
st.markdown("""
**Disclaimer:** This is not an official KEA tool. Refer to the official KEA website for authoritative information.
""")
