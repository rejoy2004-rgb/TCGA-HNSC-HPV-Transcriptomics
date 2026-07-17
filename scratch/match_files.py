import os

user_figures = [
    "Figure_1_Workflow.png",
    "HNSC_HPV_PCA.png",
    "Figure8_Volcano_DESeq2.png",
    "Plasma_Cells_Boxplot.png",
    "HNSC_HPV_CD8_Boxplot.png",
    "M0_Macrophage_Boxplot.png",
    "Revised_Immune_Heatmap.png",
    "Figure_CD8A_Validation.png",
    "Figure_CD8B_Validation.png",
    "Revised_CD8_M2_Boxplot.png",
    "HNSC_BestGene_KM.png",
    "HNSC_HPV_GO_Upregulated.png",
    "HNSC_HPV_KEGG_Downregulated.png",
    "HNSC_HPV_GSEA_dotplot.png",
    "HNSC_HPV_GO_Downregulated.png",
    "HNSC_HPV_KEGG_Upregulated.png",
    "HNSC_HPV_GSEA_ridgeplot.png"
]

intern_dir = r"C:\Users\rejoy\Documents\Intern_Project"
brain_dir = r"C:\Users\rejoy\.gemini\antigravity\brain\67335ae6-040d-491e-adcb-9f3be36881ba"

print("Checking User-Requested Filenames in Intern_Project (case-insensitive):")
intern_files = {f.lower(): f for f in os.listdir(intern_dir) if os.path.isfile(os.path.join(intern_dir, f))}

for fig in user_figures:
    fig_lower = fig.lower()
    if fig_lower in intern_files:
        actual_name = intern_files[fig_lower]
        size = os.path.getsize(os.path.join(intern_dir, actual_name))
        print(f"  {fig} -> MATCH: {actual_name} ({size} bytes)")
    else:
        print(f"  {fig} -> NO MATCH in Intern_Project")

print("\nChecking User-Requested Filenames in Brain folder (case-insensitive):")
brain_files = {f.lower(): f for f in os.listdir(brain_dir) if os.path.isfile(os.path.join(brain_dir, f))}
for fig in user_figures:
    fig_lower = fig.lower()
    if fig_lower in brain_files:
        actual_name = brain_files[fig_lower]
        size = os.path.getsize(os.path.join(brain_dir, actual_name))
        print(f"  {fig} -> MATCH in Brain: {actual_name} ({size} bytes)")
    else:
        print(f"  {fig} -> NO MATCH in Brain")
