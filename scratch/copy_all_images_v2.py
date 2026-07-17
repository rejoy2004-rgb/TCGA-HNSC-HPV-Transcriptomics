import os
import shutil
import subprocess

intern_dir = r"C:\Users\rejoy\Documents\Intern_Project"
brain_dir = r"C:\Users\rejoy\.gemini\antigravity\brain\67335ae6-040d-491e-adcb-9f3be36881ba"
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
# Source file -> Destination file in project_dir
# If source path is relative, we look in intern_dir.
# If source path starts with "brain:", we look in brain_dir.
mappings = {
    # Main figures
    "HNSC_HPV_PCA.png": "HNSC_HPV_PCA.png",
    "Figure8_Volcano_DESeq2.png": "Figure8_Volcano_DESeq2.png",
    "Plasma_Cells_Boxplot.png": "Plasma_Cells_Boxplot.png",
    "HNSC_HPV_CD8_Boxplot.png": "HNSC_HPV_CD8_Boxplot.png",
    "M2_Macrophage_Boxplot.png": "M0_Macrophage_Boxplot.png", # M2 boxplot used for M0 figure
    "HNSC_HPV_Immune_Heatmap.png": "Revised_Immune_Heatmap.png", # Heatmap
    "Figure_CD8A_Validation.png": "Figure_CD8A_Validation.png",
    "Figure_CD8B_Validation.png": "Figure_CD8B_Validation.png",
    "Revised_CD8_M2_Boxplot.png": "Revised_CD8_M2_Boxplot.png",
    "HNSC_BestGene_KM.png": "HNSC_BestGene_KM.png",
    
    # Enrichment figures (using user-uploaded versions from brain directory to avoid blank files)
    "brain:media__1782412599208.png": "HNSC_HPV_GO_Upregulated.png",  # User-uploaded GO Upregulated
    "KEGG_dotplot_Subtype.png": "HNSC_HPV_KEGG_Downregulated.png",   # Non-blank KEGG Downregulated from project
    "brain:media__1782412653474.png": "HNSC_HPV_GSEA_dotplot.png",   # User-uploaded GSEA dotplot
    
    # Supplementary
    "GO_dotplot_Subtype.png": "HNSC_HPV_GO_Downregulated.png",        # Non-blank GO Downregulated from project
    "HNSC_HPV_KEGG_Upregulated.png": "HNSC_HPV_KEGG_Upregulated.png", # Keep as is (blank/placeholder in project)
    "HNSC_HPV_GSEA_ridgeplot.png": "HNSC_HPV_GSEA_ridgeplot.png"
}

# 3. Copy files
print("\nCopying figures to workspace:")
for src_name, dst_name in mappings.items():
    if src_name.startswith("brain:"):
        actual_src = os.path.join(brain_dir, src_name.split(":", 1)[1])
    else:
        actual_src = os.path.join(intern_dir, src_name)
        
    dst_path = os.path.join(project_dir, dst_name)
    
    if os.path.exists(actual_src):
        size = os.path.getsize(actual_src)
        if size > 0:
            shutil.copy2(actual_src, dst_path)
            print(f"  Copied {src_name} ({size} bytes) -> {dst_name}")
        else:
            print(f"  Warning: Source file {src_name} is 0 bytes! Skipping.")
    else:
        print(f"  Error: Source file {src_name} (path: {actual_src}) not found!")
