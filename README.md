# pfei-efficiency-index

PF Efficiency Index (PFEI) – a nonlinear metric for evaluating the structural efficiency and robustness of systematic trading and risk management systems, based on profit factor, trade win rate, tick win rate and loss structure.

## Why PFEI?

PFEI is designed to answer practical questions such as:

- Is my current trading style structurally efficient, or does my profit factor mainly depend on luck and outliers?
- How risky is it to push my profit factor higher by using more aggressive parameters?
- Which combination of tick win rate, trade win rate, risk–reward ratio and loss-sequence length fits my personal risk tolerance?
- How can I compare different trading systems (retail, discretionary or algorithmic) on a single structural quality scale?
- How do my historical results look when they are mapped into zones like PERFECT, OPTIMAL or CATASTROPHIC – and which parameter sets make my risk measurably more efficient and sustainable over time?
  
## Overview

The PFEI measures how efficiently an observed profit factor (PF) is generated
relative to trade win rate (WT), tick win rate (WS) and the length of loss
sequences (NL). It classifies systems into structural quality zones:

- PERFECT
- OPTIMAL
- MEDIOCRE
- POOR / OVERSTRETCHED
- CATASTROPHIC

This repository contains the reference implementation in Python and example
analyses (parameter grids and Monte Carlo simulations).

## Files

- `faib_pfei_analysis_R0.py` – main Python script with PFEI definition,
  grid evaluation and Monte Carlo analysis.
- `LICENSE` – MIT license for this project.
- `README.md` – this documentation.

## Usage

Run `faib_pfei_analysis_R0.py` in a Python environment with NumPy, pandas
and Plotly installed to:

- compute PFEI for arbitrary PF, WS, WT and NL combinations,
- generate full parameter grids and zone statistics,
- create example visualizations (e.g. PFEI heatmaps).

## License

This project is licensed under the MIT License – see the `LICENSE` file.

Keywords: trading, quantitative-finance, algorithmic-trading, performance-metric, profit-factor, expectancy, risk-management, prop-trading, FAIB, PF Efficiency Index, PFEI.
