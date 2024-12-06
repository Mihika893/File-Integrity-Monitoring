# File-Integrity-Monitoring
This Python-based system monitors assigned files and directories, notifying you of any changes.

## Features:
- Tracks file permission and hash changes.
- Prompts user for action on detected changes.
- Logs timestamp of modifications.
- Automatically updates baseline after authorized changes.

Download & Navigate to the FIM_system Folder
To run it, use: `python3 ./FIMS.py`

If no changes are detected, you're notified:

![File integrity checked, no changes found](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/kr29x81iliztvsmnqui8.jpg)

If changes occur, you decide whether they're authorized:

![changes found by file integrity monitoring system](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/avopfbubpzrjcm85jzfl.jpg)

If authorized, the baseline (which stores details like filename, permissions, and hashes) updates accordingly.

![FIM system notification, baseline updated ](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/q5v9ynzepk5fkbpbqga7.jpg)

If unauthorized, a report.txt is generated, logging the modifications for investigation.

![unauthorized changes found by FIM system](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/zlr6ri6kmm5r6e7msi3q.jpg)

this is what report.txt looks like:

![report.txt will record unauthorized changes](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/tyd6i2mm4zqtfuv59h65.jpg)

To get started, clone the repo, modify the paths in **create_baseline.py** file.

![Modifying the paths in create_baseline.py accordingly](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/wsx4s27wfqec6cz4vtc3.jpg)

run it to set up a baseline for monitoring: 
`python3 ./create_baseline.py`

This will create baseline.csv file and snapshot directory.

also modify the paths in **FIMS.py** file.

![Modifying the paths in FIMS.py accordingly](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/5uydfg4qoiudoi5w20by.jpg)

we mention some files to monitor in create_baseline.py separately and also mentioned a directory to monitor in FIMS.py
all done, run the script : `python3 ./FIMS.py`
