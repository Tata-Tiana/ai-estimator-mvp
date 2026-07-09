"""Add the parent directory (earthworks_parser_google_stage1) to sys.path so that
modules like review_workbook_builder, source_paths, config etc. can be imported
without package installation."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
