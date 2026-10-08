"""Experimento: ¿qué cuantil conviene comprometer?

Entrena el mismo GBM con pérdida pinball para varios cuantiles τ, hace backtest en los últimos días y
grafica el costo en dólares y el MAE frente a τ. La teoría dice:
  · el MAE se minimiza en τ = 0,5 (la mediana)
  · el COSTO se minimiza en τ* = α_exc / (α_exc + α_falt) ≈ 0,29

Uso (después de correr la liga al menos una vez, con --demo o con datos reales):
  python -m experimentos.cuantil_optimo --dias 10
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from sklearn.ensemble import HistGradientBoostingRegressor  # noqa: E402

from liga import datos  # noqa: E402
from liga.config import CUANTIL_OPTIMO  # noqa: E402
from liga.mercado import costo_desvio_usd  # noqa: E402

sys.path.insert(0, str(datos.RAIZ / "modelos"))
from _ml_comun import entrenamiento, features  # noqa: E402

TAUS = [0.10, 0.20, 0.29, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dias", type=int, default=10)
    a = ap.parse_args()
    hist, _ = datos.cargar()
    fechas = sorted(hist.fecha_hora.dt.date.unique())[-a.dias:]
    costo, mae = {t: 0.0 for t in TAUS}, {t: [] for t in TAUS}
    for d in fechas:
        h = hist[hist.fecha_hora.dt.date < d - dt.timedelta(days=1)]
        dia = hist[hist.fecha_hora.dt.date == d].sort_values("fecha_hora")
        X, y = entrenamiento(h)
        for t in TAUS:
            m = HistGradientBoostingRegressor(loss="quantile", quantile=t, max_iter=150, learning_rate=0.08,
                                              max_leaf_nodes=15, min_samples_leaf=20, random_state=0).fit(X, y)
            p = np.clip(m.predict(features(dia)), 0, None)
            costo[t] += costo_desvio_usd(dia.eolica_mwh, p, dia.precio_cop_kwh).sum()
            mae[t].append(np.abs(p - dia.eolica_mwh.to_numpy()).mean())
        print(f"  {d} ✓")
    c = np.array([costo[t] / len(fechas) for t in TAUS]); e = np.array([np.mean(mae[t]) for t in TAUS])
    print("\n  τ     USD/día   MAE (MWh)")
    for t, ci, ei in zip(TAUS, c, e):
        print(f"  {t:.2f}  {ci:8,.0f}   {ei:6.2f}")
    print(f"\n  Mínimo costo en τ = {TAUS[int(c.argmin())]:.2f} (teoría {CUANTIL_OPTIMO:.2f}) · "
          f"mínimo MAE en τ = {TAUS[int(e.argmin())]:.2f} (teoría 0,50)")

    fig, ax = plt.subplots(figsize=(7.5, 4), dpi=120)
    ax.plot(TAUS, c, "o-", color="#C8745A", lw=2, label="Costo de desvío (USD/día)")
    ax.axvline(CUANTIL_OPTIMO, color="#C8745A", ls=":", label=f"τ* teórico = {CUANTIL_OPTIMO:.2f}")
    ax.set(xlabel="Cuantil comprometido τ", ylabel="USD/día", title="¿Qué cuantil conviene comprometer?")
    ax2 = ax.twinx(); ax2.plot(TAUS, e, "s--", color="#2E3A59", label="MAE (MWh)"); ax2.set_ylabel("MAE (MWh)")
    ax2.axvline(0.5, color="#2E3A59", ls=":")
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, frameon=False, fontsize=8, loc="upper center")
    ax.spines[["top"]].set_visible(False); ax2.spines[["top"]].set_visible(False)
    fig.tight_layout(); fig.savefig(Path(datos.RAIZ / "resultados" / "cuantil_optimo.png"))
    print("  Gráfica: resultados/cuantil_optimo.png")


if __name__ == "__main__":
    main()
