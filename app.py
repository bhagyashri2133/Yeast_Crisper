import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Yeast gRNA Risk Predictor",
    page_icon="🧬",
    layout="wide"
)

# ---------- Custom CSS ----------
st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
    color: white;
}

h1 {
    text-align:center;
}

textarea {
    border-radius:10px !important;
}

div.stButton > button {
    background-color:#00c6ff;
    color:white;
    border-radius:10px;
    height:3em;
    width:100%;
    font-size:18px;
}

div.stButton > button:hover {
    background-color:#0072ff;
}

.block-container {
    padding-top:2rem;
}

</style>
""", unsafe_allow_html=True)


# ---------- Load dataset ----------
@st.cache_data
def load_data():
    return pd.read_csv("grna_risk_lookup.csv.gz", compression="gzip")

df = load_data()

lookup = dict(zip(df["gRNA"], df["risk_level"]))


# ---------- Title ----------
st.title("🧬 Yeast CRISPR gRNA Off-Target Risk Predictor")
st.markdown("""
### About This Tool

This web tool helps identify potential **CRISPR guide RNA (gRNA)** sequences from a given **DNA sequence** and predicts their **off-target risk level** for the yeast *Saccharomyces cerevisiae*.

A **gRNA** is a short 20-base DNA sequence used in CRISPR experiments to guide the Cas9 enzyme to a specific location in the genome.

### How it works
1. Paste a **DNA sequence** into the input box below.
2. The tool scans the sequence and extracts all possible **20-bp gRNA candidates**.
3. Each candidate is compared with a **precomputed dataset (~893k gRNAs)**.
4. The tool predicts the **off-target risk level**:
   - 🟢 **Low Risk** – Safer for genome editing  
   - 🟡 **Medium Risk** – Moderate off-target possibility  
   - 🔴 **High Risk** – Higher chance of unintended edits

### What you will get
A table showing:
- the **20-bp gRNA sequence**
- its **predicted off-target risk level**

You can also **download the results as a CSV file** for further analysis.
""")
st.divider()


# ---------- DNA Input ----------
dna_seq = st.text_area(
    "Enter gRNA Sequence",
    height=220,
    placeholder="ATGCGTACGTAGCTAGCTAGCTAGCTAG..."
)


# ---------- Function ----------
def generate_grnas(seq):

    seq = seq.upper()
    grnas = []

    for i in range(len(seq) - 19):
        g = seq[i:i+20]

        if set(g).issubset({"A","T","G","C"}):
            grnas.append(g)

    return grnas


# ---------- Button ----------
if st.button("🔬 Find gRNAs and Predict Risk"):

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
            columns=["gRNA Sequence","Risk Level"]
        )

        # ---------- Metrics ----------
        col1,col2,col3 = st.columns(3)

        col1.metric("Total gRNAs", len(result_df))
        col2.metric("Low Risk", sum(result_df["Risk Level"]=="Low"))
        col3.metric("High Risk", sum(result_df["Risk Level"]=="High"))

        st.divider()

        st.subheader("Predicted gRNA Risk Levels")

        # ---------- Colored table ----------
        def highlight_risk(val):

            if val == "Low":
                return "background-color:#1e7f3f;color:white"

            elif val == "Medium":
                return "background-color:#c9a400;color:black"

            elif val == "High":
                return "background-color:#b30000;color:white"

            else:
                return ""

        st.dataframe(
            result_df.style.map(highlight_risk, subset=["Risk Level"]),
            use_container_width=True
        )


        # ---------- Download ----------
        csv = result_df.to_csv(index=False)

        st.download_button(
            label="⬇ Download Results",
            data=csv,
            file_name="grna_predictions.csv",
            mime="text/csv"
        )


st.divider()

st.caption(
"""
Tool developed for **Saccharomyces cerevisiae CRISPR off-target risk prediction**  
using a precomputed dataset (~893,000 gRNA sequences).
"""
)
