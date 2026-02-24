import numpy as np
import pandas as pd
import plotly.express as px


# -----------------------------
# PFEI-Funktion
# -----------------------------
def compute_pfei_from_params(pf, ws, wt, nl, eps=1e-9):
    """
    pf : Profitfaktor
    ws : Tick-Winrate  (0..1)
    wt : Trade-Winrate (0..1)
    nl : Verlustanzahl (>=1)
    """
    ws_clipped = max(ws, eps)
    wt_clipped = max(wt, eps)

    numerator   = pf * (1.0 - ws_clipped**3)
    denominator = pf * ws_clipped**3 - (1.0 - wt_clipped**2)

    if abs(denominator) < eps:
        I_struct = np.inf
    else:
        I_struct = numerator / denominator

    if nl < 2:
        n_factor = 1.0
    else:
        n_factor = 1.0 - 1.0 / np.sqrt(nl)

    return I_struct * n_factor


# -----------------------------
# Zonenzuordnung (Text)
# -----------------------------
def classify_zone(pfei):
    """
    q < 0                  -> SCHLECHT / ÜBERZOGEN
    0 <= q < 0.5625        -> PERFEKT
    0.5625 <= q < 3        -> OPTIMAL
    3 <= q < 5.25          -> MITTELMÄSSIG
    q >= 5.25              -> KATASTROPHAL
    """
    if pfei < 0:
        return "SCHLECHT / ÜBERZOGEN"
    elif 0 <= pfei < 0.5625:
        return "PERFEKT"
    elif 0.5625 <= pfei < 3:
        return "OPTIMAL"
    elif 3 <= pfei < 5.25:
        return "MITTELMÄSSIG"
    else:
        return "KATASTROPHAL"


# -----------------------------
# Zonenzuordnung (numerische ID)
# -----------------------------
def classify_zone_id(pfei):
    """
    1 -> PERFEKT
    2 -> OPTIMAL
    3 -> MITTELMÄSSIG
    4 -> SCHLECHT / ÜBERZOGEN
    5 -> KATASTROPHAL
    """
    if pfei < 0:
        return 4
    elif 0 <= pfei < 0.5625:
        return 1
    elif 0.5625 <= pfei < 3:
        return 2
    elif 3 <= pfei < 5.25:
        return 3
    else:
        return 5


# -----------------------------
# 1) Vollständiges Gitter
# -----------------------------
ws_grid = np.linspace(0.1, 0.9, 9)   # Tick-Winrate
wt_grid = np.linspace(0.1, 0.9, 9)   # Trade-Winrate
pf_grid = np.linspace(1.0, 5.0, 41)  # Profitfaktor
nl_grid = np.arange(1, 101)          # Verlustanzahl

rows = []
for ws in ws_grid:
    for wt in wt_grid:
        for pf in pf_grid:
            for nl in nl_grid:
                pfei = compute_pfei_from_params(pf, ws, wt, nl)
                zone = classify_zone(pfei)
                zone_id = classify_zone_id(pfei)
                rows.append((ws, wt, pf, nl, pfei, zone, zone_id))

matrix_df = pd.DataFrame(
    rows, columns=["WS", "WT", "PF", "NL", "PFEI", "Zone", "Zone_ID"]
)

zone_counts_grid = matrix_df["Zone"].value_counts()
print("Zonen im Gitter:")
print(zone_counts_grid)


# -----------------------------
# 2) Monte-Carlo-Simulation
# -----------------------------
n_samples = 50_000
rng = np.random.default_rng(42)

ws_mc = rng.uniform(0.1, 0.9, n_samples)
wt_mc = rng.uniform(0.1, 0.9, n_samples)
pf_mc = rng.uniform(1.0, 5.0, n_samples)
nl_mc = rng.integers(1, 101, n_samples)

pfei_vals = []
zones_mc = []
zones_mc_id = []

for i in range(n_samples):
    val = compute_pfei_from_params(pf_mc[i], ws_mc[i], wt_mc[i], nl_mc[i])
    pfei_vals.append(val)
    zones_mc.append(classify_zone(val))
    zones_mc_id.append(classify_zone_id(val))

mc_df = pd.DataFrame({"PFEI": pfei_vals, "Zone": zones_mc, "Zone_ID": zones_mc_id})

print("\nZonen in der Monte-Carlo-Simulation:")
print(mc_df["Zone"].value_counts())


# -----------------------------
# 3) „Ideal“-Parameter je Zone (global)
# -----------------------------
zone_targets = {
    "PERFEKT": (0.0 + 0.5625) / 2,
    "OPTIMAL": (0.5625 + 3.0) / 2,
    "MITTELMÄSSIG": (3.0 + 5.25) / 2,
}

def best_central_params_for_zone(df, zone_name, top_n=10):
    df_zone = df[df["Zone"] == zone_name].copy()
    if df_zone.empty:
        return df_zone
    target = zone_targets[zone_name]
    df_zone["dist_to_target"] = (df_zone["PFEI"] - target).abs()
    df_zone = df_zone.sort_values("dist_to_target", ascending=True)
    return df_zone.head(top_n)[
        ["WS", "WT", "PF", "NL", "PFEI", "Zone", "Zone_ID", "dist_to_target"]
    ]

best_perfect_central = best_central_params_for_zone(matrix_df, "PERFEKT", top_n=10)
best_optimal_central = best_central_params_for_zone(matrix_df, "OPTIMAL", top_n=10)
best_medium_central  = best_central_params_for_zone(matrix_df, "MITTELMÄSSIG", top_n=10)

print("\nTop-Parameter (zentral) PERFEKT:")
print(best_perfect_central)
print("\nTop-Parameter (zentral) OPTIMAL:")
print(best_optimal_central)
print("\nTop-Parameter (zentral) MITTELMÄSSIG:")
print(best_medium_central)


# -----------------------------
# 4) Visualisierungen (global)
# -----------------------------
zone_df = zone_counts_grid.reset_index()
zone_df.columns = ["Zone", "Count"]
zone_df["Share"] = zone_df["Count"] / zone_df["Count"].sum()

fig_zones = px.bar(zone_df, x="Zone", y="Share", text="Share")
fig_zones.update_traces(texttemplate="%{text:.2%}", textposition="outside")
fig_zones.update_yaxes(title_text="Anteil", tickformat=".0%")
fig_zones.update_xaxes(title_text="PFEI-Zone")
fig_zones.update_layout(title="Anteil der PFEI-Zonen im Parameterraum")
fig_zones.show()

fig_mc = px.histogram(mc_df, x="PFEI", color="Zone",
                      nbins=100, barmode="overlay")
fig_mc.update_xaxes(title_text="PFEI")
fig_mc.update_yaxes(title_text="Häufigkeit")
fig_mc.update_layout(title="Monte-Carlo-Verteilung des PFEI nach Zonen")
fig_mc.show()



# ----------------------------------------------------------
# 5) NEU: Realistischer Filter NL < 10, WT 0.3-0.8, WS 0.5-0.8, PF 1.5-3.0
# ----------------------------------------------------------
filtered_df = matrix_df[
    (matrix_df["NL"] < 20) &
    (matrix_df["WT"].between(0.3, 0.65)) &
    (matrix_df["WS"].between(0.3, 0.9)) &
    (matrix_df["PF"].between(1.1, 1.8))
].copy()


print("\nZonen im gefilterten Subraum (NL < 20, 0.3 <= WT <= 0.65, 0.3 <= WS <= 0.9, 1,1 < PF < 2):")
print(filtered_df["Zone"].value_counts())

# Beste Kombinationen im gefilterten Raum, nach PFEI sortiert
def best_in_filtered(df, zone_name, top_n=10):
    df_zone = df[df["Zone"] == zone_name].copy()
    if df_zone.empty:
        return df_zone
    df_zone = df_zone.sort_values("PFEI", ascending=False)
    return df_zone.head(top_n)[["WS", "WT", "PF", "NL", "PFEI", "Zone"]]

best_filt_perfect = best_in_filtered(filtered_df, "PERFEKT", top_n=10)
best_filt_optimal = best_in_filtered(filtered_df, "OPTIMAL", top_n=10)
best_filt_medium  = best_in_filtered(filtered_df, "MITTELMÄSSIG", top_n=10)

print("\nGefilterte Top-Kombinationen PERFEKT:")
print(best_filt_perfect)

print("\nGefilterte Top-Kombinationen OPTIMAL:")
print(best_filt_optimal)

print("\nGefilterte Top-Kombinationen MITTELMÄSSIG:")
print(best_filt_medium)
