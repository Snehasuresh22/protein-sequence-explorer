import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from analysis import analyze_fasta, init_db, save_to_db, run_blast, generate_pdf_report

st.set_page_config(page_title="Protein Explorer", layout="wide")
st.title("Protein Sequence Explorer & History")

init_db()

# Sidebar: pH input and history
st.sidebar.header("📜 Analysis History")
user_pH = st.sidebar.slider("pH for Charge Calculation", min_value=0.0, max_value=14.0, value=7.0, step=0.1)

# File upload
uploaded_file = st.file_uploader("Upload FASTA file", type=["fa", "fasta"])

if uploaded_file is not None:
    # Read FASTA content once (used for both analysis and BLAST)
    fasta_str = uploaded_file.read().decode("utf-8")
    uploaded_file.seek(0)  # Reset pointer for further reading

    # Analyze uploaded file
    df, aa_df = analyze_fasta(uploaded_file, user_pH=user_pH)
    st.subheader("Current Analysis")
    st.dataframe(df)

    st.subheader("Amino Acid Composition (%)")
    st.dataframe(aa_df.round(2))

    # --- Interactive Plotly Chart ---
    st.subheader("🧪 Interactive Chart: Amino Acid % Composition")
    aa_long = aa_df.T.reset_index()
    aa_long.columns = ["Amino Acid", "Percentage"]
    fig = px.bar(
        aa_long, x="Amino Acid", y="Percentage",
        color="Amino Acid", text="Percentage",
        title="Amino Acid Composition",
        labels={"Percentage": "%", "Amino Acid": "Residue"}
    )
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    st.plotly_chart(fig, use_container_width=True)

    # Save results to DB
    save_to_db(uploaded_file.name, df)

    # --- PDF Export ---
    st.subheader("📄 Export Report")
    pdf_buffer = generate_pdf_report(df, aa_df)
    st.download_button(
        label="📥 Download PDF Report",
        data=pdf_buffer,
        file_name="protein_analysis_report.pdf",
        mime="application/pdf"
    )

    # --- NCBI BLAST Section ---
    with st.expander("🔍 Run NCBI BLAST Search"):
        if st.button("Run BLAST Search"):
            st.info("Running BLASTp against NCBI... please wait ⏳")
            try:
                blast_df = run_blast(fasta_str)
                st.success("BLAST search complete.")
                st.subheader("Top Homologs Found")
                st.dataframe(blast_df)
            except Exception as e:
                st.error(f"BLAST failed: {e}")
else:
    st.info("Please upload a FASTA file to analyze.")

st.write("---")
st.write("*(Analysis powered by Biopython, Pandas, Streamlit, Plotly, and SQLite)*")

# --- Load history from SQLite ---
conn = sqlite3.connect("analyses.db")
history_df = pd.read_sql_query("""
    SELECT filename, length, molecular_weight, isoelectric_point,
           aromaticity, instability_index, gravy, charge_at_pH, timestamp
    FROM analysis_history ORDER BY id DESC
""", conn)
conn.close()

# Sidebar: download + view history
if not history_df.empty:
    st.sidebar.download_button(
        label="⬇️ Download Full History (CSV)",
        data=history_df.to_csv(index=False),
        file_name="protein_analysis_history.csv",
        mime="text/csv"
    )
    st.sidebar.dataframe(history_df)

    st.subheader("📊 Protein Trends from Upload History")
    st.line_chart(history_df[["instability_index", "gravy"]])
else:
    st.sidebar.info("No analysis history yet.")

