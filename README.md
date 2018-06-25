Find duplicate files!

The way this script works:
1. The script traverses all files in all folders starting from the root. For each new file found,
hashes the file's size and puts the file's full path into a bucket.
It is obvious that files with different sizes are not similar, so this step narrows the comparison
by eliminating the first possible way that makes files distinct.

2. Next the script iterates over the buckets in the dictionary created in step 1, and hashes each file's first
1KBs, putting each file's full path in the appropriate bucket.
This step is a bit of an optimization. Since if two files differ on their first chunk, we shouldn't look
into the other chunks.

3. Now the actual comparison occurs - the script will now iterate over the buckets created in step 2, and hashes each
file entirely. If two file hashes are equal in this step, it means the files are entirely identical.

4. The script will iterate over the each bucket from step 3 (each bucket represents duplicate files), and prints all
duplicate files by bucket.

# Requirements
- Python 3.2 or higher.

# Running the app

```python dffinder.py <root_path>```