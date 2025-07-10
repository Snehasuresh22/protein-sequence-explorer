from Bio import SeqIO
from Bio.SeqUtils.ProtParam import ProteinAnalysis
import pandas as pd
from io import StringIO
import sqlite3
from datetime import datetime

def analyze_fasta(fasta_file, user_pH=7.0):
    fasta_str = fasta_file.read().decode("utf-8")
    record = SeqIO.read(StringIO(fasta_str), "fasta")
    seq_str = str(record.seq)

    pa = ProteinAnalysis(seq_str)
    stats = {
        "length": len(seq_str),
        "molecular_weight": pa.molecular_weight(),
        "isoelectric_point": pa.isoelectric_point(),
        "aromaticity": pa.aromaticity(),
        "instability_index": pa.instability_index(),
        "gravy": pa.gravy(),
        "charge_at_pH": pa.charge_at_pH(user_pH)
    }

    # Amino acid composition
    aa_percent = pa.get_amino_acids_percent()
    aa_df = pd.DataFrame([aa_percent]) * 100

    return pd.DataFrame([stats]), aa_df

def init_db():
    conn = sqlite3.connect("analyses.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            length INTEGER,
            molecular_weight REAL,
            isoelectric_point REAL,
            aromaticity REAL,
            instability_index REAL,
            gravy REAL,
            charge_at_pH REAL,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_to_db(filename, df):
    conn = sqlite3.connect("analyses.db")
    c = conn.cursor()
    row = df.iloc[0]
    c.execute('''
        INSERT INTO analysis_history (
            filename, length, molecular_weight, isoelectric_point,
            aromaticity, instability_index, gravy, charge_at_pH, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        filename,
        row['length'],
        row['molecular_weight'],
        row['isoelectric_point'],
        row['aromaticity'],
        row['instability_index'],
        row['gravy'],
        row['charge_at_pH'],
        datetime.now().isoformat(timespec='seconds')
    ))
    conn.commit()
    conn.close()
    
from Bio.Blast import NCBIWWW, NCBIXML

def run_blast(fasta_str, top_n=5):
    result_handle = NCBIWWW.qblast("blastp", "nr", fasta_str, format_type="XML", hitlist_size=top_n)
    blast_record = NCBIXML.read(result_handle)

    hits = []
    for alignment in blast_record.alignments:
        hsp = alignment.hsps[0]
        identity = (hsp.identities / hsp.align_length) * 100
        hit = {
            "accession": alignment.accession,
            "organism": alignment.hit_def.split(" >")[0],
            "e_value": hsp.expect,
            "identity_percent": round(identity, 2)
        }
        hits.append(hit)

    return pd.DataFrame(hits)

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
from datetime import datetime

def generate_pdf_report(df, aa_df, filename="report.pdf"):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Protein Sequence Analysis Report")

    c.setFont("Helvetica", 10)
    c.drawString(50, height - 70, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    y = height - 100
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Summary Metrics:")
    y -= 20

    c.setFont("Helvetica", 10)
    for col in df.columns:
        val = str(df[col].values[0])
        c.drawString(60, y, f"{col}: {val}")
        y -= 15

    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Amino Acid Composition (%):")
    y -= 20

    c.setFont("Helvetica", 10)
    for aa, val in aa_df.iloc[0].items():
        c.drawString(60, y, f"{aa}: {val:.2f}%")
        y -= 12
        if y < 100:
            c.showPage()
            y = height - 50

    c.save()
    buffer.seek(0)
    return buffer

