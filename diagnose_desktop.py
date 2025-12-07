import os

desktop_path = r"C:\Users\USER\Desktop\AGENTIC AI Projects\Content Agent\main.py"

print(f"Checking: {desktop_path}")

if os.path.exists(desktop_path):
    size = os.path.getsize(desktop_path)
    print(f"Size: {size} bytes")
    
    if size > 0:
        try:
            with open(desktop_path, 'r', encoding='utf-8') as f:
                print("--- First 5 lines ---")
                for i in range(5):
                    print(f.readline().strip())
                print("---------------------")
        except Exception as e:
            print(f"Error reading file: {e}")
    else:
        print("File is empty (0 bytes).")
else:
    print("File does NOT exist.")
