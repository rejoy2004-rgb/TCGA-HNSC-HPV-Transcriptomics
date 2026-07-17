import os
import shutil
import subprocess

intern_dir = r"C:\Users\rejoy\Documents\Intern_Project"
project_dir = r"C:\Users\rejoy\.gemini\antigravity\scratch\hnsc_docx_generator"

# 1. Run plot_workflow.py to generate workflow image in project directory
print("Running plot_workflow.py...")
try:
    subprocess.run(["python", "plot_workflow.py"], cwd=project_dir, check=True)
    # Rename workflow image to matching casing
    src_flow = os.path.join(project_dir, "figure_1_workflow.png")
    dst_flow = os.path.join(project_dir, "Figure_1_Workflow.png")
    if os.path.exists(src_flow):
        shutil.move(src_flow, dst_flow)
        print("Generated and renamed Figure_1_Workflow.png")
except Exception as e:
    print(f"Error running plot_workflow.py: {e}")

# 2. Define the exact mapping of figures requested by user
# Source file in Intern_Project -> Destination file in project_dir
mappings = {
    "HNSC_HPV_PCA.png": "HNSC_HPV_PCA.png",
    "Figure8_Volcano_DESeq2.png": "Figure8_Volcano_DESeq2.png",
    "Plasma_Cells_Boxplot.png": "Plasma_Cells_Boxplot.png",
    "HNSC_HPV_CD8_Boxplot.png": "HNSC_HPV_CD8_Boxplot.png",
    "M2_Macrophage_Boxplot.png": "M0_Macrophage_Boxplot.png", # M2 boxplot is used for Figure 6 M0_Macrophage_Boxplot
    "HNSC_HPV_Immune_Heatmap.png": "Revised_Immune_Heatmap.png", # Heatmap
    "Figure_CD8A_Validation.png": "Figure_CD8A_Validation.png",
    "Figure_CD8B_Validation.png": "Figure_CD8B_Validation.png",
    "Revised_CD8_M2_Boxplot.png": "Revised_CD8_M2_Boxplot.png",
    "HNSC_BestGene_KM.png": "HNSC_BestGene_KM.png",
    "HNSC_HPV_GO_Upregulated.png": "HNSC_HPV_GO_Upregulated.png",
    "HNSC_HPV_KEGG_Downregulated.png": "HNSC_HPV_KEGG_Downregulated.png",
    "HNSC_HPV_GSEA_dotplot.png": "HNSC_HPV_GSEA_dotplot.png",
    # Supplementary
    "HNSC_HPV_GO_Downregulated.png": "HNSC_HPV_GO_Downregulated.png",
    "HNSC_HPV_KEGG_Upregulated.png": "HNSC_HPV_KEGG_Upregulated.png",
    "HNSC_HPV_GSEA_ridgeplot.png": "HNSC_HPV_GSEA_ridgeplot.png"
}

# 3. Copy files
print("\nCopying figures from Intern_Project to workspace:")
for src_name, dst_name in mappings.items():
    src_path = os.path.join(intern_dir, src_name)
    dst_path = os.path.join(project_dir, dst_name)
    
    if os.path.exists(src_path):
        size = os.path.getsize(src_path)
        if size > 0:
            shutil.copy2(src_path, dst_path)
            print(f"  Copied {src_name} ({size} bytes) -> {dst_name}")
        else:
            print(f"  Warning: Source file {src_name} is 0 bytes! Skipping.")
    else:
        print(f"  Error: Source file {src_name} not found in Intern_Project!")

# 4. Clean up old figure files with names like figure_X_... to avoid confusion
print("\nCleaning up old figure files from workspace:")
for f in os.listdir(project_dir):
    if f.startswith("figure_") and f.endswith(".png") and f != "figure_1_workflow.png":
        try:
            os.remove(os.path.join(project_dir, f))
            print(f"  Removed {f}")
        except Exception as e:
            print(f"  Error removing {f}: {e}")
