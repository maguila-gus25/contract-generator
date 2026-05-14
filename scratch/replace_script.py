def main():
    file_path = "/Users/gustavoramos/Documents/GitHub/contract-generator/frontend/index.html"
    new_script_path = "/Users/gustavoramos/Documents/GitHub/contract-generator/scratch/new_script.txt"
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    with open(new_script_path, "r", encoding="utf-8") as f:
        new_script = f.read()

    start_idx = content.find("<script>")
    end_idx = content.find("</script>") + len("</script>")
    
    if start_idx != -1 and end_idx > start_idx:
        new_content = content[:start_idx] + new_script + content[end_idx:]
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("Successfully replaced <script> block.")
    else:
        print("Could not find <script> block.")

if __name__ == "__main__":
    main()
