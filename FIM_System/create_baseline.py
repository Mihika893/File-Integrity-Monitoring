import hashlib
import os
import csv
import pwd  # To get file owner

def compute_sha256(file_path):
    """Compute SHA256 hash of the specified file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        return "File not found"
    except Exception as e:
        return f"Error: {e}"
    
def get_file_permissions(file_path):
    """Get file permissions of the specified file."""
    try:
        return oct(os.stat(file_path).st_mode)[-3:]  # Get the file permissions in octal format
    except FileNotFoundError:
        return "File not found"
    except Exception as e:
        return f"Error: {e}"

def get_file_owner(file_path):
    """Get file owner of the specified file."""
    try:
        return pwd.getpwuid(os.stat(file_path).st_uid).pw_name
    except FileNotFoundError:
        return "File not found"
    except Exception as e:
        return f"Error: {e}"

def create_snapshot(file_path, snapshot_dir):
    """Create snapshot of the specified file."""
    snapshot_path = os.path.join(snapshot_dir, os.path.basename(file_path) + '.snapshot')
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            with open(snapshot_path, 'w') as snapshot_file:
                snapshot_file.write(content)
        print(f"Snapshot created for {file_path} at {snapshot_path}")
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
    except Exception as e:
        print(f"Error creating snapshot for {file_path}: {e}")

# assign data
file_paths = [
    ["file1", "/home/Downloads/FIM_System/file1"], 
    ["file2", "/home/Downloads/FIM_System/file2"], 
    ["file3", "/home/Downloads/FIM_System/file3"]
]

# Directory to store snapshots
snapshot_dir = '/home/Downloads/FIM_System/snapshots'
os.makedirs(snapshot_dir, exist_ok=True)  # Ensure snapshot directory exists

# Create a list to store the data
mydata = []
for file_name, file_path in file_paths:
    file_hash = compute_sha256(file_path)
    file_permissions = get_file_permissions(file_path)
    file_owner = get_file_owner(file_path)
    data_row = [file_name, file_path, file_permissions, file_owner, file_hash]
    mydata.append(data_row)
    
    # Create snapshot
    create_snapshot(file_path, snapshot_dir)

# Write the data to baseline.csv
csv_file = 'baseline.csv'
with open(csv_file, 'w') as file:
    csvwriter = csv.writer(file)
    field = ["File", "Location", "File Permission", "File Owner", "File Hash (Sha256)"]
    csvwriter.writerow(field)
    for row in mydata:
        csvwriter.writerow(row)

print(f"Baseline.csv and snapshots created successfully in {snapshot_dir}.")
