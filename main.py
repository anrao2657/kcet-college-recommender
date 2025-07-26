import streamlit as st
import pandas as pd

# Load the cutoff data CSV
@st.cache_data
def load_data(csv_path='kcet_cutoffs.csv'):
    df = pd.read_csv(csv_path)
    # Ensure 'Cut-Off Rank' is numeric for filtering
    df['Cut-Off Rank'] = pd.to_numeric(df['Cut-Off Rank'], errors='coerce')
    df.dropna(subset=['Cut-Off Rank'], inplace=True)
    df['College'] = df['College'].astype(str)
    df['Category'] = df['Category'].astype(str)
    df['Course Name'] = df['Course Name'].astype(str)
    return df

df = load_data()

st.set_page_config(page_title="KCET College Recommender", layout="wide")
st.title("KCET Cut-Off Rank College Recommender")

st.markdown(
    """
    Enter your **KCET rank** and (optionally) filter by partial college name or exact category code, to see the best-matching colleges and courses.<br>
    Results show **all courses where your rank meets the cutoff**.
    """, unsafe_allow_html=True
)

# Main user input
rank = st.number_input("Enter your KCET Rank:", min_value=1, step=1, format="%d")

with st.expander("🔎 Advanced Filters (optional)"):
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        college_options = sorted(df['College'].unique())
        college_query = st.selectbox("Select College (optional)", [""] + college_options)
    with col2:
        category_options = sorted(df['Category'].unique())
        category_query = st.selectbox("Select Category (optional)", [""] + category_options)
    with col3:
        course_query = st.text_input("Search Course (type at least 3 letters)", "")
    city_query = st.text_input("Search City (type at least 3 letters)", "")

filtered_df = df.copy()

# Apply exact match filters
if college_query:
    filtered_df = filtered_df[filtered_df['College'] == college_query]

if category_query:
    filtered_df = filtered_df[filtered_df['Category'] == category_query]

if course_query and len(course_query.strip()) >= 3:
    filtered_df = filtered_df[
        filtered_df['Course Name'].str.lower().str.startswith(course_query.strip().lower())
    ]

if city_query and len(city_query.strip()) >= 3:
    city_query_lower = city_query.strip().lower()
    filtered_df = filtered_df[
        filtered_df['College'].apply(
            lambda name: name.split(",")[-1].strip().lower().startswith(city_query_lower)
        )
    ]

# Sort filtered dataframe before filtering rank qualification
filtered_df = filtered_df.sort_values(
    by=['Cut-Off Rank', 'College', 'Course Name'], ascending=[True, True, True]
).reset_index(drop=True)

# Apply rank filtering after college and category filters
# ✅ Correct logic: You qualify if your rank is less than or equal to the cutoff
recommended = filtered_df[filtered_df['Cut-Off Rank'] >= rank]

if recommended.empty:
    st.warning("No colleges found matching your rank and filter criteria.")
else:
    st.header(f"Recommended Colleges for Rank {int(rank)}")
    st.dataframe(
        recommended[['College', 'Course Name', 'Category', 'Cut-Off Rank']],
        use_container_width=True,
        hide_index=True
    )
    # Download button for filtered data
    csv = recommended.to_csv(index=False)
    st.download_button(
        label="Download results as CSV",
        data=csv,
        file_name=f"kcet_college_recommendations_rank_{int(rank)}.csv",
        mime='text/csv'
    )

# Disclaimer section
st.markdown("---")
st.markdown(
    "**Disclaimer:** This is not an official KEA tool. It is built for informational purposes only. "
    "Please always refer to the [official KEA website](https://cetonline.karnataka.gov.in/kea/ugcet2025) for authoritative and up-to-date information."
)