import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_summary_figure():
    fig, ax = plt.subplots(figsize=(7.5, 4.2), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis('off')

    # Draw Title
    ax.text(
        5, 4.6, "Immune Microenvironment Remodeling in HPV-Positive HNSC",
        ha='center', va='center', fontsize=12, fontweight='bold', color='#1e1b4b',
        fontname='DejaVu Sans'
    )

    # 1. Left Box: Enriched Populations
    # Round rectangle patch
    rect_left = patches.FancyBboxPatch(
        (0.5, 0.4), 4.2, 3.6, boxstyle="round,pad=0.1",
        fc='#ecfdf5', ec='#059669', lw=1.5, mutation_scale=0.2
    )
    ax.add_patch(rect_left)

    # Header for Left Box
    ax.text(
        2.6, 3.6, "Enriched Infiltrates\n(Humoral & Cytotoxic Activation)",
        ha='center', va='center', fontsize=10, fontweight='bold', color='#065f46',
        fontname='DejaVu Sans'
    )

    # Items for Left Box
    left_items = [
        "▲  Plasma Cells\n    (Median 0.440 vs. 0.140; FDR = 0.001)",
        "▲  CD8+ T Cells\n    (Median 0.070 vs. 0.048; FDR = 0.020)",
        "▲  B Cells (Naïve & Memory)\n    (Active Humoral Immunity; log2FC > 1)"
    ]
    y_left = [2.7, 1.8, 0.9]
    for item, y in zip(left_items, y_left):
        ax.text(
            0.8, y, item,
            ha='left', va='center', fontsize=8.5, fontweight='bold', color='#0f766e',
            fontname='DejaVu Sans'
        )

    # 2. Right Box: Depleted Populations
    rect_right = patches.FancyBboxPatch(
        (5.3, 0.4), 4.2, 3.6, boxstyle="round,pad=0.1",
        fc='#fff5f5', ec='#e11d48', lw=1.5, mutation_scale=0.2
    )
    ax.add_patch(rect_right)

    # Header for Right Box
    ax.text(
        7.4, 3.6, "Depleted Infiltrates\n(Reduced Immunosuppressed/Resting States)",
        ha='center', va='center', fontsize=10, fontweight='bold', color='#991b1b',
        fontname='DejaVu Sans'
    )

    # Items for Right Box
    right_items = [
        "▼  M0 Macrophages\n    (Median 0.030 vs. 0.103; FDR = 0.002)",
        "▼  Resting NK Cells\n    (Median 0.005 vs. 0.029; FDR = 0.009)",
        "▼  Resting CD4+ Memory T Cells\n    (Median 0.041 vs. 0.068; FDR = 0.013)"
    ]
    y_right = [2.7, 1.8, 0.9]
    for item, y in zip(right_items, y_right):
        ax.text(
            5.6, y, item,
            ha='left', va='center', fontsize=8.5, fontweight='bold', color='#be123c',
            fontname='DejaVu Sans'
        )

    plt.tight_layout()
    plt.savefig('HNSC_Immune_Summary.png', bbox_inches='tight', dpi=300)
    plt.close()
    print("Successfully generated HNSC_Immune_Summary.png")

if __name__ == "__main__":
    generate_summary_figure()
