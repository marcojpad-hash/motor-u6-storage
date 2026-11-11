#!/usr/bin/env python3
"""Vista de precesión — descriptiva, no concluyente (apartado en espera).

Dibuja, para Mozart y Napoleón, la trayectoria (x_tusi, y_transversal, año)
como una hélice: en cada corte un anillo pequeño y un palito que apunta en
la dirección unitaria del paso al siguiente corte. El tercer panel marca el
ángulo desenrollado del palito, las aristas y los pares con dirección casi
igual (|Δ| < 20°). No analiza ni concluye.
"""

from __future__ import annotations

import csv
import textwrap
from io import BytesIO
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import Normalize
from matplotlib.lines import Line2D
from matplotlib.patches import Ellipse
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from PIL import Image

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "coordenadas_modelo_externo"
OUT = HERE
TITLE = "Vista de precesión — descriptiva, no concluyente (apartado en espera)"
CASES = (
    ("Mozart", DATA / "tabla_coordenadas_mozart.csv", "MOZART_VISTA_PRECESION.png"),
    ("Napoleón", DATA / "tabla_coordenadas_napoleon.csv", "NAPOLEON_VISTA_PRECESION.png"),
)
CONVERGENCE_DEG = 20.0
FACE = "#f6f4f0"
AX_FACE = "#fffcf7"
CMAP_NAME = "plasma"


def load_table(path: Path) -> dict:
    with path.open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    return {
        "corte": [r["corte"] for r in rows],
        "ano": np.array([float(r["ano"]) for r in rows], float),
        "x": np.array([float(r["x_tusi"]) for r in rows], float),
        "y": np.array([float(r["y_transversal"]) for r in rows], float),
        "radio": np.array([float(r["radio"]) for r in rows], float),
        "fase": np.array([float(r["fase_grados"]) for r in rows], float),
    }


def steps_of(d: dict) -> dict:
    dx = np.diff(d["x"])
    dy = np.diff(d["y"])
    largo = np.hypot(dx, dy)
    ang = np.arctan2(dy, dx)
    return {
        "dx": dx,
        "dy": dy,
        "ux": dx / np.maximum(largo, 1e-12),
        "uy": dy / np.maximum(largo, 1e-12),
        "largo": largo,
        "ang": ang,
        "ang_deg": np.rad2deg(ang),
        "ang_unw": np.rad2deg(np.unwrap(ang)),
    }


def circdiff(a: float, b: float) -> float:
    return abs((a - b + 180.0) % 360.0 - 180.0)


def convergence_pairs(ang_deg: np.ndarray) -> list[tuple[int, int, float]]:
    pairs = []
    n = len(ang_deg)
    for i in range(n):
        for j in range(i + 1, n):
            delta = circdiff(float(ang_deg[i]), float(ang_deg[j]))
            if delta < CONVERGENCE_DEG:
                pairs.append((i, j, delta))
    return pairs


def pca_ellipse(x: np.ndarray, y: np.ndarray, nstd: float = 1.85):
    pts = np.column_stack([x, y])
    mu = pts.mean(axis=0)
    cov = np.cov(pts, rowvar=False)
    eigval, eigvec = np.linalg.eigh(cov)
    order = eigval.argsort()[::-1]
    eigval, eigvec = eigval[order], eigvec[:, order]
    theta = np.degrees(np.arctan2(eigvec[1, 0], eigvec[0, 0]))
    width, height = 2.0 * nstd * np.sqrt(np.maximum(eigval, 0))
    return mu, width, height, theta


def ring_polyline(x0: float, y0: float, r: float, n: int = 96):
    th = np.linspace(0.0, 2.0 * np.pi, n)
    return x0 + r * np.cos(th), y0 + r * np.sin(th)


def step_label(cortes: list[str], i: int) -> str:
    return f"{cortes[i]}→{cortes[i + 1]}"


def label_offsets_2d(x, y, min_sep: float, radius: float):
    """Coloca etiquetas hacia afuera del centro, con un poco de rechazo entre sí."""
    mx, my = float(np.mean(x)), float(np.mean(y))
    n = len(x)
    pos = []
    for i in range(n):
        vx, vy = float(x[i] - mx), float(y[i] - my)
        norm = max((vx * vx + vy * vy) ** 0.5, 1e-9)
        pos.append(np.array([x[i] + vx / norm * radius * 2.15, y[i] + vy / norm * radius * 2.15]))
    pos = np.array(pos, float)
    for _ in range(12):
        for i in range(n):
            for j in range(i + 1, n):
                delta = pos[i] - pos[j]
                dist = float(np.hypot(delta[0], delta[1]))
                if dist < min_sep and dist > 0:
                    push = 0.5 * (min_sep - dist) * delta / dist
                    pos[i] += push
                    pos[j] -= push
    return pos


def trim_face(arr: np.ndarray, face: str = FACE, tol: int = 14, pad: int = 10) -> np.ndarray:
    """Recorta el margen del color de fondo que deja el canvas 3D."""
    bg = (np.array(mpl.colors.to_rgb(face)) * 255.0).reshape(1, 1, 3)
    rgb = arr[:, :, :3].astype(np.float64)
    mask = np.any(np.abs(rgb - bg) > tol, axis=2)
    rows = np.where(mask.any(axis=1))[0]
    cols = np.where(mask.any(axis=0))[0]
    if len(rows) == 0 or len(cols) == 0:
        return arr
    r0 = max(0, int(rows[0]) - pad)
    r1 = min(arr.shape[0], int(rows[-1]) + 1 + pad)
    c0 = max(0, int(cols[0]) - pad)
    c1 = min(arr.shape[1], int(cols[-1]) + 1 + pad)
    return arr[r0:r1, c0:c1]


def configure_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 11.5,
            "axes.labelsize": 10,
            "axes.linewidth": 0.7,
            "xtick.labelsize": 8.5,
            "ytick.labelsize": 8.5,
            "legend.fontsize": 8,
            "figure.facecolor": FACE,
            "axes.facecolor": AX_FACE,
            "savefig.facecolor": FACE,
            "savefig.bbox": None,
        }
    )


def wrap_pairs(cortes, pairs, width=148) -> str:
    bits = [f"{step_label(cortes, i)} ≈ {step_label(cortes, j)} ({delta:.1f}°)" for i, j, delta in pairs]
    if not bits:
        return "Posible convergencia (|Δdirección| < 20°): ningún par en este umbral."
    text = "Posible convergencia (|Δdirección| < 20°): " + "   ·   ".join(bits)
    return "\n".join(textwrap.wrap(text, width=width, subsequent_indent="    "))


def draw_palito_2d(ax, cx, cy, ux, uy, length, color, zorder=6):
    x0, y0 = cx - 0.35 * length * ux, cy - 0.35 * length * uy
    x1, y1 = cx + length * ux, cy + length * uy
    ax.annotate(
        "",
        xy=(x1, y1),
        xytext=(x0, y0),
        arrowprops=dict(
            arrowstyle="-|>",
            color=color,
            lw=1.8,
            mutation_scale=11,
            shrinkA=0,
            shrinkB=0,
        ),
        zorder=zorder,
    )


def draw_palito_3d(ax, cx, cy, cz, ux, uy, length, color):
    x0, y0 = cx - 0.35 * length * ux, cy - 0.35 * length * uy
    x1, y1 = cx + length * ux, cy + length * uy
    ax.plot([x0, x1], [y0, y1], [cz, cz], color=color, lw=2.0, solid_capstyle="round", zorder=5)
    ax.scatter([x1], [y1], [cz], s=22, color=color, edgecolors="#2b2118", linewidths=0.35, zorder=6)


def render_helix_image(d, s, colors, seg_colors, lws, ring_r, palito_len) -> np.ndarray:
    """Renderiza la hélice 3D a una imagen recortada, para que no se salga de su panel."""
    x, y, years, cortes = d["x"], d["y"], d["ano"], d["corte"]
    n = len(cortes)
    fig = plt.figure(figsize=(7.2, 5.8), dpi=160, facecolor=FACE)
    ax = fig.add_subplot(111, projection="3d")
    ax.set_facecolor(FACE)
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.pane.set_facecolor((1, 1, 1, 0.46))
        axis.pane.set_edgecolor("#d8d3cb")
        axis._axinfo["grid"]["color"] = (0.6, 0.58, 0.52, 0.35)
        axis._axinfo["grid"]["linestyle"] = ":"
        axis._axinfo["grid"]["linewidth"] = 0.4

    segs3d = [np.column_stack([x[i : i + 2], y[i : i + 2], years[i : i + 2]]) for i in range(n - 1)]
    ax.add_collection3d(Line3DCollection(segs3d, colors=seg_colors, linewidths=lws, capstyle="round"))

    for i in range(n):
        cx, cy, cz = float(x[i]), float(y[i]), float(years[i])
        col = colors[i]
        rx, ry = ring_polyline(cx, cy, ring_r)
        ax.plot(rx, ry, np.full_like(rx, cz), color=col, lw=1.55, zorder=4)
        ax.scatter([cx], [cy], [cz], s=16, color=col, edgecolors="#2b2118", linewidths=0.35, zorder=5)
        if i < n - 1:
            draw_palito_3d(ax, cx, cy, cz, float(s["ux"][i]), float(s["uy"][i]), palito_len, col)

    for i in range(n):
        dt_prev = years[i] - years[i - 1] if i else 99
        side = 1 if i % 2 == 0 else -1
        extra = ring_r * (2.0 if dt_prev < 1.2 else 1.2)
        ax.text(
            float(x[i]),
            float(y[i]) + side * extra,
            float(years[i]),
            cortes[i],
            fontsize=8,
            color="#2b2118",
            ha="center",
            va="bottom" if side > 0 else "top",
        )

    span = max(float(np.ptp(x)), float(np.ptp(y)), 0.4)
    pad = 0.20 * span
    ax.set_xlim(float(x.min()) - pad, float(x.max()) + pad)
    ax.set_ylim(float(y.min()) - pad, float(y.max()) + pad)
    zpad = 0.04 * (float(years.max()) - float(years.min()))
    ax.set_zlim(float(years.min()) - zpad, float(years.max()) + zpad)
    xr = float(np.ptp(x)) + 2 * pad
    yr = float(np.ptp(y)) + 2 * pad
    ax.set_box_aspect((xr, yr, 1.55 * max(xr, yr)), zoom=1.22)
    ax.view_init(elev=17, azim=-62)
    ax.set_xlabel("x Tusi", labelpad=6)
    ax.set_ylabel("y transversal", labelpad=4)
    ax.set_zlabel("año", labelpad=6)
    ax.yaxis.set_major_locator(mpl.ticker.MaxNLocator(nbins=4))
    ax.tick_params(axis="both", labelsize=8)
    ax.tick_params(axis="z", labelsize=8)

    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=160, facecolor=FACE, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    buf.seek(0)
    arr = np.asarray(Image.open(buf).convert("RGBA"))
    return trim_face(arr, face=FACE, pad=10)


def draw_case(nombre: str, path: Path, dest: Path) -> Path:
    d = load_table(path)
    s = steps_of(d)
    x, y, years, cortes = d["x"], d["y"], d["ano"], d["corte"]
    n = len(cortes)
    cmap = plt.get_cmap(CMAP_NAME)
    norm = Normalize(vmin=float(years.min()), vmax=float(years.max()))
    colors = cmap(norm(years))
    seg_colors = cmap(norm(0.5 * (years[:-1] + years[1:])))
    span = max(float(np.ptp(x)), float(np.ptp(y)), 0.4)
    ring_r = 0.048 * span
    palito_len = 2.45 * ring_r
    pairs = convergence_pairs(s["ang_deg"])
    largos = s["largo"]
    umbral_larga = float(np.quantile(largos, 0.75))
    pair_text = wrap_pairs(cortes, pairs)
    lws = 1.7 + 3.6 * (largos / max(float(largos.max()), 1e-12))
    helix = render_helix_image(d, s, colors, seg_colors, lws, ring_r, palito_len)

    fig = plt.figure(figsize=(16, 10), dpi=100)
    fig.patch.set_facecolor(FACE)
    gs = fig.add_gridspec(
        2,
        2,
        height_ratios=[1.22, 1.0],
        width_ratios=[1.12, 1.0],
        left=0.048,
        right=0.975,
        top=0.868,
        bottom=0.145,
        wspace=0.14,
        hspace=0.30,
    )
    ax3d = fig.add_subplot(gs[0, 0])
    ax2d = fig.add_subplot(gs[0, 1])
    axang = fig.add_subplot(gs[1, :])

    # ── Panel 1: hélice 3D (imagen recortada) ──────────────────────────
    ax3d.set_facecolor(FACE)
    ax3d.imshow(helix)
    ax3d.set_xlim(-0.5, helix.shape[1] - 0.5)
    ax3d.set_ylim(helix.shape[0] - 0.5, -0.5)
    ax3d.axis("off")
    ax3d.margins(0)
    ax3d.set_aspect("equal")
    ax3d.set_title("Hélice (x, y, año) — anillo y palito en cada corte", pad=6)

    # ── Panel 2: vista desde arriba ────────────────────────────────────
    ax2d.set_facecolor(AX_FACE)
    ax2d.axhline(0, color="#b7b1a6", lw=0.7, ls="--", zorder=0, label="eje Tusi (y = 0)")
    mu, width, height, theta = pca_ellipse(x, y)
    ell = Ellipse(
        mu,
        width,
        height,
        angle=theta,
        facecolor="none",
        edgecolor="#8a8478",
        lw=1.15,
        ls="--",
        zorder=1,
        label="elipse que recorre (ajuste descriptivo)",
    )
    ax2d.add_patch(ell)
    for i in range(n - 1):
        ax2d.plot(
            x[i : i + 2],
            y[i : i + 2],
            color=seg_colors[i],
            lw=float(lws[i]),
            solid_capstyle="round",
            zorder=2,
        )
    for i in range(n):
        cx, cy = float(x[i]), float(y[i])
        col = colors[i]
        rx, ry = ring_polyline(cx, cy, ring_r)
        ax2d.plot(rx, ry, color=col, lw=1.7, zorder=4)
        ax2d.scatter([cx], [cy], s=22, color=col, edgecolors="#2b2118", linewidths=0.4, zorder=5)
        if i < n - 1:
            draw_palito_2d(ax2d, cx, cy, float(s["ux"][i]), float(s["uy"][i]), palito_len, col)

    lab_pos = label_offsets_2d(x, y, min_sep=0.11 * span, radius=ring_r)
    for i in range(n):
        ax2d.text(
            lab_pos[i, 0],
            lab_pos[i, 1],
            cortes[i],
            fontsize=8,
            color="#2b2118",
            ha="center",
            va="center",
            zorder=7,
        )

    # Límites justos al trazo, la elipse y las etiquetas (sin inflar el eje x).
    x0, x1 = ax2d.get_xlim()
    y0, y1 = ax2d.get_ylim()
    xs = np.concatenate([x, lab_pos[:, 0], np.array([x0, x1])])
    ys = np.concatenate([y, lab_pos[:, 1], np.array([y0, y1])])
    # Incluye el recuadro de la elipse rotada.
    ell_verts = ell.get_path().transformed(ell.get_patch_transform()).vertices
    xs = np.concatenate([xs, ell_verts[:, 0]])
    ys = np.concatenate([ys, ell_verts[:, 1]])
    pad2 = 0.08 * span
    ax2d.set_xlim(float(xs.min()) - pad2, float(xs.max()) + pad2)
    ax2d.set_ylim(float(ys.min()) - pad2, float(ys.max()) + pad2)
    ax2d.set_aspect("equal", adjustable="box")
    ax2d.set_anchor("W")
    ax2d.set_xlabel("x Tusi")
    ax2d.set_ylabel("y transversal")
    ax2d.set_title("Vista desde arriba (x, y) — palitos y elipse que recorre", pad=8)
    ax2d.grid(True, linestyle=":", linewidth=0.45, color="#c9c3b8", alpha=0.85)
    ax2d.legend(
        loc="lower right",
        frameon=True,
        fancybox=False,
        edgecolor="#d0cbc3",
        fontsize=7.5,
    )
    for spine in ax2d.spines.values():
        spine.set_color("#c9c3b8")

    # ── Panel 3: ángulo del palito vs año ──────────────────────────────
    axang.set_facecolor(AX_FACE)
    start_years = years[:-1]
    end_years = years[1:]
    ang = s["ang_unw"]
    y_bot, y_top = float(ang.min()), float(ang.max())
    y_rng = max(y_top - y_bot, 20.0)
    axang.set_ylim(y_bot - 0.18 * y_rng, y_top + 0.16 * y_rng)
    axang.set_xlim(float(years.min()) - 0.6, float(years.max()) + 0.6)

    mid_years = 0.5 * (start_years + end_years)
    axlen = axang.twinx()
    year_span = float(years.max() - years.min()) or 1.0
    bw = max(0.32, 0.030 * year_span)
    bar_colors = [(*seg_colors[i][:3], 0.58 if largos[i] >= umbral_larga else 0.26) for i in range(n - 1)]
    axlen.bar(
        mid_years,
        largos,
        width=bw,
        color=bar_colors,
        edgecolor="#5a544c",
        linewidth=0.4,
        zorder=1,
        align="center",
    )
    axlen.set_ylabel("largo del paso (arista en x, y)")
    axlen.set_ylim(0, float(largos.max()) * 2.55)
    axlen.tick_params(axis="y", labelsize=8)
    axlen.spines["top"].set_visible(False)

    pair_years = sorted({float(start_years[i]) for i, _, _ in pairs} | {float(start_years[j]) for _, j, _ in pairs})
    for py in pair_years:
        axang.axvline(py, color="#2b6b5a", lw=0.8, ls="--", alpha=0.38, zorder=2)

    for i in range(n - 1):
        axang.plot(
            [start_years[i], end_years[i]],
            [ang[i], ang[i]],
            color=seg_colors[i],
            lw=2.4 if largos[i] >= umbral_larga else 1.6,
            solid_capstyle="round",
            zorder=4,
            alpha=0.95,
        )
    axang.plot(start_years, ang, color="#3d2f4f", lw=1.15, zorder=5, alpha=0.85)
    for i in range(n - 1):
        size = 42 + 95 * (largos[i] / max(float(largos.max()), 1e-12))
        axang.scatter(
            [start_years[i]],
            [ang[i]],
            s=size,
            color=seg_colors[i],
            edgecolors="#2b2118",
            linewidths=0.55,
            zorder=6,
        )

    sides = []
    for i in range(n - 1):
        prefer = 1 if ang[i] <= (y_bot + y_top) / 2 else -1
        if sides and abs(start_years[i] - start_years[i - 1]) < max(1.3, 0.04 * year_span):
            prefer = -sides[-1]
        sides.append(prefer)

    for i in range(n - 1):
        is_long = largos[i] >= umbral_larga
        label = f"{step_label(cortes, i)}\n{largos[i]:.2f}"
        if is_long:
            label += "  arista larga"
        va = "bottom" if sides[i] > 0 else "top"
        axang.text(
            start_years[i],
            ang[i] + sides[i] * 0.055 * y_rng,
            label,
            ha="center",
            va=va,
            fontsize=6.7,
            color="#2b2118",
            fontweight="bold" if is_long else "normal",
            zorder=7,
        )

    axang.set_xlabel("año")
    axang.set_ylabel("ángulo del palito (°), desenrollado")
    axang.set_title(
        "Ángulo del palito y largo de las aristas  ·  el tramo horizontal es la duración del paso",
        pad=8,
    )
    axang.grid(True, linestyle=":", linewidth=0.45, color="#c9c3b8", alpha=0.85)
    axang.spines["top"].set_visible(False)
    for spine in ("left", "bottom"):
        axang.spines[spine].set_color("#c9c3b8")

    legend_elems = [
        Line2D([0], [0], color="#3d2f4f", lw=1.3, label="ángulo del palito (desenrollado)"),
        Line2D([0], [0], color="#8a6bb0", lw=7, alpha=0.4, label="largo del paso (barra más opaca = arista larga)"),
        Line2D([0], [0], color="#2b6b5a", lw=1.1, ls="--", alpha=0.7, label="posible convergencia (corte de un par con |Δ| < 20°)"),
    ]
    axang.legend(
        handles=legend_elems,
        loc="upper left",
        frameon=True,
        fancybox=False,
        edgecolor="#d0cbc3",
        fontsize=7.4,
        ncol=1,
        bbox_to_anchor=(0.0, 1.0),
        borderaxespad=0.35,
    )

    fig.text(
        0.048,
        0.078,
        pair_text,
        fontsize=7.3,
        color="#21584b",
        ha="left",
        va="top",
        linespacing=1.35,
        family="DejaVu Sans",
    )

    sm = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    cax = fig.add_axes([0.855, 0.922, 0.12, 0.016])
    cb = fig.colorbar(sm, cax=cax, orientation="horizontal")
    cb.set_label("año", fontsize=8, labelpad=1)
    cb.ax.tick_params(labelsize=7)

    fig.suptitle(f"{TITLE}\n{nombre}", fontsize=15.5, color="#2b2118", y=0.975)
    fig.text(
        0.048,
        0.012,
        "El palito es el vector unitario del paso en el plano (x Tusi, y transversal).  "
        "El grosor de cada arista sigue su largo.  Apartado en espera de más casos.",
        fontsize=7.2,
        color="#5a544c",
        ha="left",
        va="bottom",
    )

    # Ajusta el ancho del panel 3D a la proporción real de la hélice
    # y cede el espacio sobrante a la vista desde arriba.
    fig.canvas.draw()
    p3d = ax3d.get_position()
    p2d = ax2d.get_position()
    fig_w, fig_h = fig.get_size_inches()
    img_aspect = helix.shape[0] / helix.shape[1]
    new_w = p3d.height * fig_h / img_aspect / fig_w
    ax3d.set_position([p3d.x0, p3d.y0, new_w, p3d.height])
    gap = 0.018
    new_x0 = p3d.x0 + new_w + gap
    ax2d.set_position([new_x0, p2d.y0, p2d.x1 - new_x0, p2d.height])

    dest.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(dest, dpi=100, facecolor=FACE)
    plt.close(fig)
    print(nombre)
    print("  pares:", pair_text.replace("\n", " "))
    print("  largos:", ", ".join(f"{step_label(cortes, i)}={largos[i]:.3f}" for i in range(n - 1)))
    print("  umbral arista larga (p75):", round(umbral_larga, 3))
    return dest


def main() -> None:
    configure_style()
    for nombre, src, fname in CASES:
        out = draw_case(nombre, src, OUT / fname)
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
