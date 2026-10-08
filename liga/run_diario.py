"""Corre la liga completa: datos → predicciones de todos los modelos → calificación en USD → leaderboard.

Uso:
  python -m liga.run_diario                  # modo real (API XM + Open-Meteo)
  python -m liga.run_diario --demo           # datos sintéticos, sin internet
  python -m liga.run_diario --backtest 14    # además re-evalúa los últimos 14 días (arranque en frío)
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import time
from zoneinfo import ZoneInfo

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from . import datos  # noqa: E402
from .config import ALFA_EXCEDENTE, ALFA_FALTANTE, CAPACIDAD_MW, CUANTIL_OPTIMO, PARQUE, TRM  # noqa: E402
from .mercado import costo_desvio_usd, valor_energia_usd  # noqa: E402

RAIZ = datos.RAIZ
PRED = RAIZ / "predicciones"
RES = RAIZ / "resultados"
BASE = "Persistencia"


# ---------------------------------------------------------------- modelos
def cargar_modelos() -> dict:
    modelos = {}
    for f in sorted((RAIZ / "modelos").glob("*.py")):
        if f.name.startswith("_"):
            continue
        spec = importlib.util.spec_from_file_location(f.stem, f)
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
            modelos[getattr(mod, "NOMBRE", f.stem)] = mod
        except Exception as e:  # noqa: BLE001
            print(f"  ⚠ {f.name} no carga: {e}")
    return modelos


def correr(modelos: dict, historia: pd.DataFrame, clima_dia: pd.DataFrame) -> dict:
    salida = {}
    for nombre, mod in modelos.items():
        t0 = time.time()
        try:
            y = np.asarray(mod.predecir(historia.copy(), clima_dia.copy()), dtype=float).ravel()
            if y.shape != (24,) or not np.isfinite(y).all():
                raise ValueError(f"devolvió forma {y.shape} o valores no finitos")
            salida[nombre] = np.clip(y, 0, CAPACIDAD_MW)           # no se puede comprometer más que la capacidad
            print(f"  ✓ {nombre:<30} {time.time() - t0:5.1f}s")
        except Exception as e:  # noqa: BLE001
            print(f"  ✗ {nombre:<30} falló: {e}")
    return salida


def clima_de(clima: pd.DataFrame, dia: dt.date) -> pd.DataFrame:
    c = clima[clima.fecha_hora.dt.date == dia].sort_values("fecha_hora").reset_index(drop=True)
    if len(c) != 24:
        raise RuntimeError(f"No hay pronóstico completo de viento para {dia}")
    return c


# ---------------------------------------------------------------- predicción del día
def predecir_manana(hist, clima, modelos):
    manana = dt.datetime.now(ZoneInfo("America/Bogota")).date() + dt.timedelta(days=1)
    print(f"\n▶ Compromiso oficial para {manana} (último dato XM: {hist.fecha_hora.max():%Y-%m-%d})")
    archivo = PRED / f"{manana}.csv"
    previo = pd.read_csv(archivo) if archivo.exists() else pd.DataFrame({"hora": range(24)})
    # Regla anti-trampa: la primera predicción emitida para un día NO se sobreescribe
    faltan = {k: v for k, v in modelos.items() if k not in previo.columns}
    preds = correr(faltan, hist, clima_de(clima, manana))
    for k, v in preds.items():
        previo[k] = np.round(v, 3)
    PRED.mkdir(exist_ok=True)
    previo.to_csv(archivo, index=False)


def backtest(hist, clima, modelos, n: int):
    print(f"\n▶ Backtest de los últimos {n} días")
    fechas = sorted(hist.fecha_hora.dt.date.unique())[-n:]
    filas = []
    for d in fechas:
        h = hist[hist.fecha_hora.dt.date < d - dt.timedelta(days=1)]   # simula el rezago de 2 días de XM
        print(f" {d}")
        for k, v in correr(modelos, h, clima_de(clima, d)).items():
            filas += [{"fecha": d, "hora": i, "modelo": k, "pred": x} for i, x in enumerate(v)]
    pd.DataFrame(filas).to_csv(RES / "backtest.csv", index=False)


# ---------------------------------------------------------------- calificación
def _largo_oficial() -> pd.DataFrame:
    filas = []
    for f in sorted(PRED.glob("*.csv")):
        df = pd.read_csv(f).melt(id_vars="hora", var_name="modelo", value_name="pred")
        df["fecha"] = dt.date.fromisoformat(f.stem)
        filas.append(df)
    return pd.concat(filas) if filas else pd.DataFrame(columns=["fecha", "hora", "modelo", "pred"])


def calificar(hist: pd.DataFrame, largo: pd.DataFrame) -> pd.DataFrame:
    real = hist.assign(fecha=hist.fecha_hora.dt.date, hora=hist.fecha_hora.dt.hour)[
        ["fecha", "hora", "eolica_mwh", "precio_cop_kwh"]]
    m = largo.assign(fecha=pd.to_datetime(largo.fecha).dt.date).merge(real, on=["fecha", "hora"])
    if m.empty:
        return pd.DataFrame()
    m["costo"] = costo_desvio_usd(m.eolica_mwh, m.pred, m.precio_cop_kwh)
    m["valor"] = valor_energia_usd(m.eolica_mwh, m.precio_cop_kwh)
    m["ae"] = (m.pred - m.eolica_mwh).abs()
    m["sesgo"] = m.pred - m.eolica_mwh
    dia = m.groupby(["modelo", "fecha"]).agg(costo=("costo", "sum"), valor=("valor", "sum"),
                                              mae=("ae", "mean"), sesgo=("sesgo", "mean")).reset_index()
    base = dia[dia.modelo == BASE].set_index("fecha")["costo"]
    tabla = dia.groupby("modelo").agg(dias=("fecha", "nunique"), costo_dia=("costo", "mean"),
                                      costo_total=("costo", "sum"), valor=("valor", "sum"),
                                      mae_mwh=("mae", "mean"), sesgo_mwh=("sesgo", "mean"))
    tabla["pct_valor"] = tabla.costo_total / tabla.valor
    # Skill en dólares vs persistencia, solo en los días que ambos tienen
    skill = {}
    for k, g in dia.groupby("modelo"):
        comun = g[g.fecha.isin(base.index)]
        skill[k] = 1 - comun.costo.sum() / base[comun.fecha].sum() if len(comun) and base[comun.fecha].sum() > 0 else np.nan
    tabla["skill"] = pd.Series(skill)
    return tabla.sort_values("costo_dia")


def _tabla_md(t: pd.DataFrame, autores: dict) -> str:
    if t.empty:
        return "_Aún no hay días calificados: XM publica con 1-2 días de rezago._\n"
    lin = ["| # | Modelo | Autor | Días | 💵 Costo de desvío (USD/día) | % del valor de la energía | "
           "Skill $ vs persistencia | MAE (MWh) | Sesgo (MWh) |",
           "|---|---|---|---|---|---|---|---|---|"]
    medallas = ["🥇", "🥈", "🥉"]
    for i, (k, r) in enumerate(t.iterrows()):
        pos = medallas[i] if i < 3 else str(i + 1)
        sk = "—" if k == BASE or pd.isna(r.skill) else f"{r.skill:+.1%}"
        lin.append(f"| {pos} | {k} | {autores.get(k, '?')} | {int(r.dias)} | {r.costo_dia:,.0f} | {r.pct_valor:.1%} | "
                   f"{sk} | {r.mae_mwh:.2f} | {r.sesgo_mwh:+.2f} |")
    return "\n".join(lin) + "\n"


def grafica(hist, largo, titulo, archivo):
    largo = largo.assign(fecha=pd.to_datetime(largo.fecha).dt.date)
    dias_ok = sorted(set(largo.fecha) & set(hist.fecha_hora.dt.date))
    if not dias_ok:
        return False
    d = dias_ok[-1]
    real = hist[hist.fecha_hora.dt.date == d].sort_values("fecha_hora")
    fig, ax = plt.subplots(figsize=(9, 4.4), dpi=120)
    ax.fill_between(range(24), real.eolica_mwh, color="#7FA383", alpha=.35, label="Real (XM)")
    ax.plot(range(24), real.eolica_mwh.to_numpy(), color="#3E6B48", lw=2)
    paleta = ["#C8745A", "#2E3A59", "#D9B65D", "#6D597A", "#2A6F97", "#B56576", "#43AA8B",
              "#E07A5F", "#81B29A", "#F2A541", "#5E548E", "#9C6644"]
    for i, (k, g) in enumerate(largo[largo.fecha == d].groupby("modelo")):
        ax.plot(g.hora, g.pred, lw=1.6, ls="--" if k == BASE else "-", color=paleta[i % len(paleta)], label=k)
    ax2 = ax.twinx()
    ax2.plot(range(24), real.precio_cop_kwh.to_numpy(), color="#999999", lw=1, ls=":", label="Bolsa (COP/kWh)")
    ax2.set_ylabel("Precio de bolsa (COP/kWh)", color="#777777")
    ax2.spines[["top"]].set_visible(False)
    ax.set(title=f"{titulo} — {PARQUE} — {d}", xlabel="Hora", ylabel="Generación (MWh)", xlim=(0, 23),
           ylim=(0, CAPACIDAD_MW * 1.05))
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=7, ncol=2, loc="upper left")
    fig.tight_layout()
    fig.savefig(archivo)
    plt.close(fig)
    return True


def leaderboard(hist, modelos):
    autores = {k: getattr(m, "AUTOR", "?") for k, m in modelos.items()}
    oficial = _largo_oficial()
    t_of = calificar(hist, oficial)
    bt_path = RES / "backtest.csv"
    bt = pd.read_csv(bt_path) if bt_path.exists() else pd.DataFrame()
    t_bt = calificar(hist, bt) if not bt.empty else pd.DataFrame()
    g1 = grafica(hist, oficial, "Compromiso oficial vs real", RES / "ultimo_dia.png") if not oficial.empty else False
    g2 = grafica(hist, bt, "Backtest", RES / "backtest.png") if not bt.empty else False
    ahora = dt.datetime.now(ZoneInfo("America/Bogota")).strftime("%Y-%m-%d %H:%M")
    md = [f"# 🌬️ Liga de Pronóstico Eólico Colombia — Leaderboard\n",
          f"_Actualizado: {ahora} (hora Colombia) · Parque: **{PARQUE}** ({CAPACIDAD_MW:.0f} MW) · "
          f"Gana quien **pierde menos dinero por desviaciones**: faltar cuesta {ALFA_FALTANTE:.0%} del precio de bolsa, "
          f"sobrar cuesta {ALFA_EXCEDENTE:.0%} · TRM {TRM:,.0f} · Cuantil óptimo teórico ≈ {CUANTIL_OPTIMO:.2f}_\n",
          "## 🏆 Liga oficial (compromisos hechos ANTES de conocer el dato real)\n", _tabla_md(t_of, autores)]
    if g1:
        md.append("![último día](resultados/ultimo_dia.png)\n")
    md += ["## 🧪 Backtest (días pasados, para arrancar en frío)\n",
           "_Ojo: en el backtest el 'pronóstico' de viento es casi el viento observado → resultados optimistas._\n",
           _tabla_md(t_bt, autores)]
    if g2:
        md.append("![backtest](resultados/backtest.png)\n")
    md.append("**Cómo leer la tabla:** el *sesgo* negativo significa que el modelo compromete menos de lo que genera. "
              "Con estas reglas eso **conviene** un poco: faltar castiga más que sobrar.\n")
    (RAIZ / "LEADERBOARD.md").write_text("\n".join(md), encoding="utf-8")
    print("\n" + "\n".join(md))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--backtest", type=int, default=0)
    ap.add_argument("--sin-descarga", action="store_true", help="usa datos/ ya cacheados")
    a = ap.parse_args()
    RES.mkdir(exist_ok=True)
    PRED.mkdir(exist_ok=True)
    hist, clima = datos.cargar() if a.sin_descarga else datos.actualizar(demo=a.demo)
    modelos = cargar_modelos()
    print(f"Modelos en la liga: {', '.join(modelos)}")
    predecir_manana(hist, clima, modelos)
    if a.backtest:
        backtest(hist, clima, modelos, a.backtest)
    leaderboard(hist, modelos)


if __name__ == "__main__":
    main()
