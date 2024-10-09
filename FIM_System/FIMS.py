import tkinter as tk
from tkinter import messagebox
import os
import csv
import hashlib
from datetime import datetime
import difflib
import pwd  # Import the pwd module

# Function to compute the SHA256 hash of a file
def compute_sha256(file_path):
    sha256 = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except FileNotFoundError:
        return None

# Function to get file permissions
def get_permissions(file_path):
    try:
        return oct(os.stat(file_path).st_mode)[-3:]
    except FileNotFoundError:
        return None

# Function to get file owner username
def get_owner(file_path):
    try:
        uid = os.stat(file_path).st_uid
        return pwd.getpwuid(uid).pw_name
    except FileNotFoundError:
        return None

# Function to get file content
def get_file_content(file_path):
    try:
        with open(file_path, 'r') as f:
            return f.readlines()
    except FileNotFoundError:
        return None

# Function to read baseline CSV
def read_baseline(csv_file):
    baseline = []
    if os.path.exists(csv_file):
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                baseline.append(row)
    return baseline

# Function to update baseline CSV
def update_baseline(csv_file, baseline):
    fieldnames = ['File', 'Location', 'File Permission', 'File Hash (Sha256)', 'File Owner']
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(baseline)

# Function to find content changes
def find_content_changes(old_content, new_content):
    diff = difflib.ndiff(old_content, new_content)
    changes = []
    for line in diff:
        if line.startswith('+ ') or line.startswith('- '):
            line_num = old_content.index(line[2:]) + 1 if line[2:] in old_content else new_content.index(line[2:]) + 1
            changes.append(f'"{line[2:].strip()}" at Line {line_num}')
    return changes

# Function to load snapshot
def load_snapshot(file_path, snapshot_dir):
    snapshot_path = os.path.join(snapshot_dir, os.path.basename(file_path) + '.snapshot')
    if os.path.exists(snapshot_path):
        with open(snapshot_path, 'r') as f:
            return f.readlines()
    return []

# Function to save snapshot
def save_snapshot(file_path, snapshot_dir):
    snapshot_path = os.path.join(snapshot_dir, os.path.basename(file_path) + '.snapshot')
    content = get_file_content(file_path)
    if content:
        with open(snapshot_path, 'w') as f:
            f.writelines(content)


def get_change_time(file_path):
    try:
        file_stat = os.stat(file_path)
        change_time = file_stat.st_ctime
        formatted_time = datetime.fromtimestamp(change_time).strftime('%Y-%m-%d %H:%M:%S')
        return formatted_time
    except FileNotFoundError:
        return "File not found"
    except Exception as e:
        return f"Error: {e}"


# Function to check file integrity
def check_integrity(baseline, monitored_dir, snapshot_dir):
    changes = []
    
    # Track files in the baseline
    tracked_files = {entry['Location']: entry for entry in baseline}
    
    # Check for changes in tracked files
    for entry in baseline:
        file_name = entry['File']
        file_path = entry['Location']
        expected_permissions = entry['File Permission']
        expected_hash = entry['File Hash (Sha256)']
        expected_owner = entry['File Owner']
        
        current_permissions = get_permissions(file_path)
        current_hash = compute_sha256(file_path)
        current_content = get_file_content(file_path)
        current_owner = get_owner(file_path)
        
        if current_permissions is None or current_hash is None or current_content is None or current_owner is None:
            change_type = "file deleted"
            content_changes = []
        elif current_permissions != expected_permissions or current_hash != expected_hash or current_owner != expected_owner:
            change_type = "content modified"
            old_content = load_snapshot(file_path, snapshot_dir)
            content_changes = find_content_changes(old_content, current_content)
        else:
            continue

        timestamp = get_change_time(file_path)
        
        changes.append({
            'file_name': file_name,
            'file_path': file_path,
            'expected_permissions': expected_permissions,
            'current_permissions': current_permissions,
            'expected_hash': expected_hash,
            'current_hash': current_hash,
            'expected_owner': expected_owner,
            'current_owner': current_owner,
            'content_changes': content_changes,
            'change_type': change_type,
            'timestamp': timestamp
        })
    
    # Check for new files
    for root, dirs, files in os.walk(monitored_dir):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if file_path not in tracked_files:
                current_permissions = get_permissions(file_path)
                current_hash = compute_sha256(file_path)
                current_content = get_file_content(file_path)
                current_owner = get_owner(file_path)
                
                changes.append({
                    'file_name': file_name,
                    'file_path': file_path,
                    'expected_permissions': None,
                    'current_permissions': current_permissions,
                    'expected_hash': None,
                    'current_hash': current_hash,
                    'expected_owner': None,
                    'current_owner': current_owner,
                    'content_changes': [],
                    'change_type': "new file added",
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Retrieve timestamp here
                })
                save_snapshot(file_path, snapshot_dir)
    
    return changes

# Function to show system notification and prompt for input using tkinter
def show_notification_with_tkinter(title, message):
    root = tk.Tk()
    root.withdraw()  # Hide main window

    response = messagebox.askquestion(title, message, icon='warning')
    return response == 'yes'

# Function to check if baseline.csv exists
def check_baseline_exists(baseline_file):
    if not os.path.exists(baseline_file):
        messagebox.showwarning("Baseline File Missing", f"The baseline file {baseline_file} does not exist. Please create it first.")
        return False
    return True

# Main function
def main():
    baseline_file = '/home/Downloads/FIM_System/baseline.csv'
    monitored_dir = '/home/Downloads/FIM_System/monitor'  # path to the directory you want to monitor
    snapshot_dir = '/home/Downloads/FIM_System/snapshots'  # directory to store file snapshots

    # Ensure the snapshot directory exists
    os.makedirs(snapshot_dir, exist_ok=True)

    if not check_baseline_exists(baseline_file):
        return
    
    baseline = read_baseline(baseline_file)
    changes = check_integrity(baseline, monitored_dir, snapshot_dir)
    
    if changes:
        try:
            with open("report.txt", "a") as f:
                for change in changes:
                    f.write(f"Timestamp: {change['timestamp']}\n")
                    f.write(f"File: {change['file_name']} (Path: {change['file_path']})\n")
                    f.write(f"Change type: {change['change_type']}\n")
                    f.write(f"Expected permissions: {change['expected_permissions']}, Current permissions: {change['current_permissions']}\n")
                    f.write(f"Expected hash: {change['expected_hash']}, Current hash: {change['current_hash']}\n")
                    f.write(f"Expected owner: {change['expected_owner']}, Current owner: {change['current_owner']}\n")
                    if change['change_type'] == "content modified":
                        f.write("Content changes: ")
                        f.write(", ".join(change['content_changes']))
                        f.write("\n")
                    f.write("\n")
        except Exception as e:
            print(f"Error creating report.txt: {e}")
            return
        
        authorized = show_notification_with_tkinter("File Integrity Alert", "File integrity checked, changes found, are these authorized?")
        
        if authorized:
            for change in changes:
                if change['change_type'] == "new file added":
                    baseline.append({
                        'File': change['file_name'],
                        'Location': change['file_path'],
                        'File Permission': change['current_permissions'],
                        'File Hash (Sha256)': change['current_hash'],
                        'File Owner': change['current_owner']
                    })
                elif change['change_type'] == "file deleted":
                    baseline = [entry for entry in baseline if entry['Location'] != change['file_path']]
                else:
                    for entry in baseline:
                        if entry['File'] == change['file_name']:
                            entry['File Permission'] = change['current_permissions']
                            entry['File Hash (Sha256)'] = change['current_hash']
                            entry['File Owner'] = change['current_owner']
                            save_snapshot(change['file_path'], snapshot_dir)
            update_baseline(baseline_file, baseline)
            os.remove("report.txt")
            messagebox.showinfo("Changes Authorized", "Baseline updated.")
        else:
            messagebox.showwarning("Changes Not Authorized", "Check report.txt at /home/Downloads/FIM_System/report.txt for investigation.")
    else:
        messagebox.showinfo("File Integrity Check", "File integrity checked, no changes found.")

if __name__ == '__main__':
    main()
