# Protein Sequence Explorer & Analysis Tool

This is a bioinformatics mini-project designed to analyze protein FASTA sequences using:

- Python and Streamlit for a simple web-based interface
- Biopython for sequence and protein calculations
- Plotly for interactive visualization
- SQLite to store upload history
- NCBI BLASTp integration for homolog search
- PDF report export for documentation

> Built in 3 days using Linux, WSL, Git, and GitHub for demonstration and portfolio purposes.

---

## Features

- Upload protein FASTA sequences and perform automatic analysis
- Calculate:
  - Sequence length
  - Molecular weight
  - Isoelectric point
  - Aromaticity
  - Instability index
  - GRAVY score
  - Charge at custom pH
- Amino Acid Composition table (%)
- Interactive bar chart using Plotly
- Run BLASTp (via NCBI) to retrieve homologous sequences
- Save analysis history to SQLite database
- Export data as CSV and generate a PDF report

---

## Tech Stack

| Tool         | Purpose                               |
|--------------|----------------------------------------|
| Python       | Scripting and application logic        |
| Streamlit    | Interactive web interface              |
| Biopython    | Protein analysis and FASTA parsing     |
| Pandas       | DataFrame handling and preprocessing   |
| SQLite       | Store upload history                   |
| Plotly       | Data visualization                     |
| ReportLab    | PDF generation                         |
| NCBI BLAST   | Homolog search via API                 |

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Snehasuresh22/protein-sequence-explorer.git
cd protein-sequence-explorer

