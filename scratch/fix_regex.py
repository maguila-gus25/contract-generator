import sys

def main():
    file_path = "/Users/gustavoramos/Documents/GitHub/contract-generator/frontend/index.html"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # We want to replace `/<\\/p>/g` with `/<\/p>/g`
    old_text = r"replace(/<\\/p>/g"
    new_text = r"replace(/<\/p>/g"
    
    if old_text in content:
        content = content.replace(old_text, new_text)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("Replaced successfully!")
    else:
        print("Could not find the target string.")

if __name__ == "__main__":
    main()
