"""Add the parent directory (usv_strict_pdf_parser_v3) to sys.path so that
modules like text_normalization, evidence_layer, etc. can be imported
without package installation."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
