from pathlib import Path

directory = Path("resumes")

for file in directory.iterdir():
    if file.suffix == ".pdf":
        new_name = ""
        for i in file.name:
            if i==" ":
                i = "_"
            new_name+=i
        
        print(f"Renamed: {file.name} → {new_name}")
