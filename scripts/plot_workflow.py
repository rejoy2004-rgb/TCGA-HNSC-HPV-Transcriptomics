import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_workflow():
    # Set up figure
    fig, ax = plt.subplots(figsize=(8.5, 11), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Background color
    fig.patch.set_facecolor('white')
    
    # Title
    ax.text(
        5, 11.5, "Bioinformatics Analysis Pipeline Workflow",
        ha='center', va='center', fontsize=14, fontweight='bold', color='#1e1b4b',
        fontname='DejaVu Sans'
    )
    
    # Bbox styling helpers
    def get_bbox(fill, border):
        return dict(boxstyle="round,pad=0.6,rounding_size=0.15", fc=fill, ec=border, lw=1.5)
        
    # Text styling helpers
    def get_text_style(fill, border, text_color, size=10):
        return dict(ha='center', va='center', fontsize=size, fontweight='bold', color=text_color, fontname='DejaVu Sans', bbox=get_bbox(fill, border))

    # Box definitions (x, y, text, style)
    boxes = [
        # Blue - Input & Prep (Tailwind sky colors)
        (5, 10.5, "TCGA-HNSC Primary Dataset\n(566 Patient Cases)", get_text_style('#f0f9ff', '#0284c7', '#0369a1', size=11)),
        (5, 9.3, "HPV Status Annotation\n(Genomically & Clinically Stratified)", get_text_style('#f0f9ff', '#0284c7', '#0369a1', size=11)),
        (5, 8.1, "Sample Filtering & Matching\n(n = 279: 243 HPV-Negative, 36 HPV-Positive)", get_text_style('#f0f9ff', '#0284c7', '#0369a1', size=11)),
        
        # Green - Core differential expression (Tailwind green colors)
        (5, 6.9, "Differential Expression Analysis\n(DESeq2 Package)", get_text_style('#f0fdf4', '#16a34a', '#15803d', size=11)),
        
        # Orange/Gold - Analyses (Tailwind orange colors)
        (2.4, 5.3, "Immune Cell Deconvolution\n(CIBERSORTx / LM22 Matrix)", get_text_style('#fff7ed', '#ea580c', '#c2410c', size=10)),
        (7.6, 5.3, "Functional & Pathway Analysis\n• GO & KEGG (clusterProfiler)\n• GSEA (fgsea)", get_text_style('#fff7ed', '#ea580c', '#c2410c', size=10)),
        
        # Purple - Survival (Tailwind purple colors)
        (5, 3.7, "Survival & Prognostic Modelling\n(Cox Regression & Kaplan-Meier;\nsurvival Package)", get_text_style('#faf5ff', '#9333ea', '#7e22ce', size=11)),
        
        # Coral/Red - Findings (Tailwind red colors)
        (5, 1.7, "Major Biological Findings\n• Humoral Infiltration (Plasma cells ↑)\n• Cellular Cytotoxicity (CD8+ T cells ↑)\n• Muted Myeloid Microenvironment (M0 cells ↓)\n• Epithelial Barrier Depletion (Keratinisation ↓)", get_text_style('#fef2f2', '#dc2626', '#b91c1c', size=11))
    ]
    
    # Plot all boxes
    for x, y, text, style in boxes:
        ax.text(x, y, text, **style)
        
    # Draw Arrows
    arrow_style = dict(arrowstyle="-|>", color='#475569', lw=2.0, mutation_scale=15)
    
    # 1 -> 2
    ax.annotate('', xy=(5, 9.75), xytext=(5, 10.05), arrowprops=arrow_style)
    # 2 -> 3
    ax.annotate('', xy=(5, 8.55), xytext=(5, 8.85), arrowprops=arrow_style)
    # 3 -> 4
    ax.annotate('', xy=(5, 7.35), xytext=(5, 7.65), arrowprops=arrow_style)
    
    # Branching 4 -> 5a and 5b
    ax.annotate('', xy=(2.4, 5.75), xytext=(4.6, 6.45), arrowprops=arrow_style)
    ax.annotate('', xy=(7.6, 5.75), xytext=(5.4, 6.45), arrowprops=arrow_style)
    
    # Merging 5a and 5b -> 6
    ax.annotate('', xy=(4.6, 4.15), xytext=(2.4, 4.85), arrowprops=arrow_style)
    ax.annotate('', xy=(5.4, 4.15), xytext=(7.6, 4.85), arrowprops=arrow_style)
    
    # 6 -> 7
    ax.annotate('', xy=(5, 2.5), xytext=(5, 3.25), arrowprops=arrow_style)
    
    plt.tight_layout()
    plt.savefig('Figure_1_Workflow.png', bbox_inches='tight', dpi=300)
    plt.close()
    print("Successfully generated Figure_1_Workflow.png")

if __name__ == "__main__":
    generate_workflow()
