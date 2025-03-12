import zipfile
import json
import os

# Step 1: Extract the .sb2 file
input_file = "13-6_project.sb2"  # 원본 스크래치 파일 경로
output_dir = "extracted_project_13_6"  # 임시 디렉토리
os.makedirs(output_dir, exist_ok=True)

with zipfile.ZipFile(input_file, 'r') as zip_ref:
    zip_ref.extractall(output_dir)

# Step 2: Locate and parse the JSON file
project_json_path = os.path.join(output_dir, 'project.json')
with open(project_json_path, 'r', encoding='utf-8') as file:
    project_data = json.load(file)

# Step 3: Modify the JSON for the required functionality
children_data = project_data.get('children', [])
snowball_sprite = next((child for child in children_data if child.get('objName') == '눈덩이'), None)
arrow_sprite = next((child for child in children_data if child.get('objName') == '화살표'), None)

if snowball_sprite:
    # Add scripts to the "눈덩이" sprite
    snowball_sprite['scripts'] = [
        [
            10,
            20,
            [
                ["whenGreenFlag"],
                ["hide"],
                ["switchCostumeTo:", "눈덩이1"],
                ["goToFront"]
            ]
        ],
        [
            20,
            20,
            [
                ["whenKeyPressed", "space"],
                ["show"],
                ["goTo:", "화살표"],
                ["repeatUntil", ["touching:", "벽"], [
                    ["move:", 10]
                ]],
                ["if", ["touching:", "눈사람"], [
                    ["broadcast:", "맞음"],
                    ["hide"]
                ]],
                ["if", ["not", ["touching:", "눈사람"]], [
                    ["hide"]
                ]]
            ]
        ]
    ]

if arrow_sprite:
    # Add scripts to the "화살표" sprite
    arrow_sprite['scripts'] = [
        [
            10,
            20,
            [
                ["whenGreenFlag"],
                ["forever", [
                    ["move:", 10],
                    ["ifOnEdgeBounce"]
                ]]
            ]
        ]
    ]

# Step 4: Save the modified JSON
with open(project_json_path, 'w', encoding='utf-8') as file:
    json.dump(project_data, file, indent=2)

# Step 5: Repackage the .sb2 file
modified_sb2_path = "modified_project_13_6.sb2"  # 최종 파일 저장 경로
with zipfile.ZipFile(modified_sb2_path, 'w') as zip_ref:
    for foldername, subfolders, filenames in os.walk(output_dir):
        for filename in filenames:
            file_path = os.path.join(foldername, filename)
            arcname = os.path.relpath(file_path, output_dir)
            zip_ref.write(file_path, arcname)

print(f"Modified project saved as {modified_sb2_path}")
