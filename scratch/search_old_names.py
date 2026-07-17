old_names = [
    "figure_1_workflow.png",
    "figure_2_pca.png",
    "figure_3_volcano.png",
    "figure_4_plasma_cells.png",
    "figure_5_cd8_t_cells.png",
    "figure_6_m0_macrophages.png",
    "figure_7_heatmap.png",
    "figure_8_cd8a_corr.png",
    "figure_9_cd8b_corr.png",
    "figure_10_cd8_m2_ratio.png",
    "figure_11_survival.png"
]

with open("generate_docx.py", "r", encoding="utf-8") as f:
    content = f.read()

for name in old_names:
    matches = [i for i in range(len(content)) if content.startswith(name, i)]
    if matches:
        print(f"Old name '{name}' found at positions: {matches}")
        # Print line numbers
        lines = content.split("\n")
        for idx, line in enumerate(lines):
            if name in line:
                print(f"  Line {idx+1}: {line.strip()}")
