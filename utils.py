import matplotlib.pyplot as plt
import matplotlib.patches as patches

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