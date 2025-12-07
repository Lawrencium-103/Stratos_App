import shutil
import os

source_dir = os.getcwd()
dest_dir = r"C:\Users\USER\Desktop\AGENTIC AI Projects\Content Agent"

files_to_copy = ["main.py", "strategist.py"]

print(f"Copying files from {source_dir} to {dest_dir}...")

if not os.path.exists(dest_dir):
    print(f"Destination directory does not exist: {dest_dir}")
else:
    for file in files_to_copy:
        src = os.path.join(source_dir, file)
        dst = os.path.join(dest_dir, file)
        try:
            shutil.copy2(src, dst)
            print(f"✅ Copied {file}")
        except Exception as e:
            print(f"❌ Failed to copy {file}: {e}")

    # Copy prompts folder
    src_prompts = os.path.join(source_dir, "prompts")
    dst_prompts = os.path.join(dest_dir, "prompts")
    try:
        if os.path.exists(dst_prompts):
            shutil.rmtree(dst_prompts)
        shutil.copytree(src_prompts, dst_prompts)
        print("✅ Copied prompts folder")
    except Exception as e:
        print(f"❌ Failed to copy prompts: {e}")

print("Done.")
