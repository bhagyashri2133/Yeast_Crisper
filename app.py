import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Yeast gRNA Risk Predictor",
    page_icon="🧬",
    layout="wide"
)

# Load lookup table
# Load compressed dataset
df = pd.read_csv("grna_risk_lookup.csv.gz", compression="gzip")

lookup = dict(zip(df["gRNA"], df["risk_level"]))

st.title("🧬 Yeast CRISPR gRNA Off-Target Risk Predictor")

st.markdown("""
Paste a **DNA sequence** below.  
The tool will automatically extract all **20-bp gRNA candidates**  
and predict their **off-target risk level**.

Risk categories:

🟢 Low Risk  
🟡 Medium Risk  
🔴 High Risk
""")

st.divider()

# DNA sequence input
dna_seq = st.text_area(
    "Paste DNA sequence",
    height=200,
    placeholder="ATGCGTACGTAGCTAGCTAGCTAGCTAG..."
)

# Function to extract 20bp guides
def generate_grnas(seq):

    seq = seq.upper()
    grnas = []

    for i in range(len(seq) - 19):
        grna = seq[i:i+20]

        if set(grna).issubset({"A","T","G","C"}):
            grnas.append(grna)

    return grnas


# Prediction button
if st.button("Find gRNAs and Predict Risk"):

    dna_seq = dna_seq.replace("\n","").upper()

    if len(dna_seq) < 20:
        st.error("Sequence must be at least 20 bp long")

    else:

        guides = generate_grnas(dna_seq)

        results = []

        for g in guides:

            if g in lookup:
                risk = lookup[g]
            else:
                risk = "Not Found"

            results.append([g, risk])

        result_df = pd.DataFrame(
            results,
            columns=["gRNA Sequence", "Risk Level"]
        )

        st.subheader("Predicted gRNA Risk Levels")

        st.dataframe(result_df, use_container_width=True)

        # Download results
        csv = result_df.to_csv(index=False)

        st.download_button(
            label="Download Results",
            data=csv,
            file_name="grna_predictions.csv",
            mime="text/csv"
        )

st.divider()

st.caption(
"Tool built for yeast (Saccharomyces cerevisiae) CRISPR off-target risk prediction using a precomputed dataset of ~893k gRNA sequences."
)
