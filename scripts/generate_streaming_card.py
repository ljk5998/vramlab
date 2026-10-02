"""Render the streaming report card with the existing typography system."""
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from generate_social_cards import Card, MARGIN

card = Card(Path('C:/Windows/Fonts'))
card.text('VRAM Lab', MARGIN, 48, 31, color='#438FE5', bold=True)
card.text('Streaming on WSL2', MARGIN, 138, 66, bold=True)
card.text('Cache and repeated reads', MARGIN, 235, 43, color='#C4C4BC')
card.chips(('CSV', 'Parquet', 'Empty and reused caches'), 350)
card.text('60 fresh processes', MARGIN, 475, 29, bold=True)
card.text('Measured 2026-10-02', 700, 475, 26, color='#C4C4BC')
card.footer()
card.save(Path(__file__).resolve().parents[1] / 'static/images/og-hf-streaming-wsl2.png')
