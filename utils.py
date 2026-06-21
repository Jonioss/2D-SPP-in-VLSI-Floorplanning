import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.lines as mlines

def plot_packing(x, y, w, h, chip_width, H):
    fig, ax = plt.subplots(figsize=(8, 6))

    # Outer strip
    ax.add_patch(
        patches.Rectangle((0, 0), chip_width, H,
                          edgecolor='black', facecolor='none', linewidth=2)
    )

    # Inner rectangles
    for i in range(len(x)):
        rect = patches.Rectangle(
            (x[i], y[i]), w[i], h[i],
            edgecolor='black', facecolor='skyblue', alpha=0.7, linewidth=1.5
        )
        ax.add_patch(rect)

        ax.text(
            x[i] + w[i] / 2,
            y[i] + h[i] / 2,
            f"R{i}",
            ha='center', va='center', fontsize=10
        )

    ax.set_xlim(0, chip_width)
    ax.set_ylim(0, H)
    ax.set_aspect('equal')
    ax.set_title(f"Strip Packing Result (H = {H:.2f})")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True, linestyle='--', alpha=0.3)
    plt.tight_layout()
    plt.show()

def plot_packing_full(x, y, w, h, chip_width, H,
                 nets=None, units_wh=None, roti=None):
    """
    Plot strip packing result.  When nets/units_wh/roti are supplied the
    function also draws pins and wires so you can see how well the
    wirelength objective pulled connected blocks together.
 
    Parameters
    ----------
    x, y        : block lower-left coordinates (lists of floats)
    w, h        : effective block widths/heights *after* rotation (lists)
    chip_width  : fixed strip width
    H           : strip height (solution value)
    nets        : list of net dicts  {'pins': [(block_idx, ox, oy), …],
                                      'weight': float}
    units_wh    : original (unrotated) block dimensions  [[w0,h0], …]
    roti        : rotation primal values  [0.0 or 1.0, …]
    """
 
    n = len(x)
    show_wires = (nets is not None
                  and units_wh is not None
                  and roti is not None)
 
    # ── figure + axes ────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(10, 7))
 
    # ── outer strip ──────────────────────────────────────────────────────────
    ax.add_patch(patches.Rectangle(
        (0, 0), chip_width, H,
        edgecolor='black', facecolor='none', linewidth=2
    ))
 
    # ── blocks ───────────────────────────────────────────────────────────────
    for i in range(n):
        ax.add_patch(patches.Rectangle(
            (x[i], y[i]), w[i], h[i],
            edgecolor='#2c3e50', facecolor='#aed6f1',
            alpha=0.75, linewidth=1.5
        ))
        ax.text(
            x[i] + w[i] / 2, y[i] + h[i] / 2, f"R{i}",
            ha='center', va='center',
            fontsize=9, fontweight='bold', color='#1a252f'
        )
 
    # ── wires ────────────────────────────────────────────────────────────────
    if show_wires:
        num_nets = len(nets)
 
        # one colour per net from a qualitative colourmap
        cmap  = plt.cm.get_cmap('tab10', max(num_nets, 1))
        hpwl  = 0.0
        legend_handles = []
 
        for k, net in enumerate(nets):
            color = cmap(k)
            pins  = []                          # (global_x, global_y) per pin
 
            # ── compute pin global positions ──────────────────────────────
            for (bi, ox, oy) in net['pins']:
                wi_b, hi_b = units_wh[bi]
                rotated    = roti[bi] > 0.5
 
                if rotated:                     # 90° CW rotation
                    px = x[bi] + hi_b - oy
                    py = y[bi] + ox
                else:
                    px = x[bi] + ox
                    py = y[bi] + oy
 
                pins.append((px, py))
 
            if not pins:
                continue
 
            xs_pins = [p[0] for p in pins]
            ys_pins = [p[1] for p in pins]
 
            # ── HPWL bounding box (dashed, lightly filled) ───────────────
            bx = min(xs_pins);  bw = max(xs_pins) - bx
            by = min(ys_pins);  bh = max(ys_pins) - by
            ax.add_patch(patches.Rectangle(
                (bx, by), bw, bh,
                edgecolor=color, facecolor=color,
                alpha=0.07, linewidth=1.2,
                linestyle='--', zorder=2
            ))
 
            hpwl += bw + bh
 
            # ── wires between pins ────────────────────────────────────────
            if len(pins) == 2:
                # 2-pin net → direct line
                ax.plot(
                    [pins[0][0], pins[1][0]],
                    [pins[0][1], pins[1][1]],
                    color=color, linewidth=1.8, alpha=0.85, zorder=3
                )
            else:
                # multi-pin net → star from centroid (avoids clutter)
                cx = sum(xs_pins) / len(pins)
                cy = sum(ys_pins) / len(pins)
                ax.plot(cx, cy, '+', color=color,
                        markersize=7, markeredgewidth=1.5, zorder=4)
                for px, py in pins:
                    ax.plot(
                        [cx, px], [cy, py],
                        color=color, linewidth=1.8, alpha=0.85, zorder=3
                    )
 
            # ── pin markers ───────────────────────────────────────────────
            for px, py in pins:
                ax.plot(px, py, 'o',
                        color='white', markersize=6, zorder=5)
                ax.plot(px, py, 'o',
                        color=color,   markersize=4, zorder=6)
 
            # ── legend entry ──────────────────────────────────────────────
            legend_handles.append(mlines.Line2D(
                [], [], color=color, linewidth=2,
                marker='o', markersize=5,
                label=f'Net {k}'
            ))
 
        # ── legend + HPWL annotation ──────────────────────────────────────
        if legend_handles:
            ax.legend(
                handles=legend_handles,
                loc='upper right', fontsize=8,
                framealpha=0.9, edgecolor='#cccccc'
            )
 
        title = (f"Strip Packing + Wirelength  "
                 f"(H = {H:.2f},  HPWL = {hpwl:.2f})")
    else:
        title = f"Strip Packing Result  (H = {H:.2f})"
 
    # ── axes formatting ───────────────────────────────────────────────────────
    ax.set_xlim(-0.5, chip_width + 0.5)
    ax.set_ylim(-0.5, H * 1.08)           # small top margin for legend
    ax.set_aspect('equal')
    ax.set_title(title, fontsize=11)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True, linestyle='--', alpha=0.25)
 
    plt.tight_layout()
    plt.show()