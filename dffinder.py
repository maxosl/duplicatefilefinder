import sys
import os
import hashlib
import logging


# create a dictionary mapping file sizes to their paths
def make_by_size_dict(root):
    by_size_dict = {}

    for path in root:
        for dirs, _, files in os.walk(path):
            for file in files:
                file_path = os.path.join(dirs, file)
                try:
                    file_size = os.path.getsize(path)
                except OSError:
                    logging.warning('Error in path %s: could not get size for %s' % (path, file))
                    continue

                duplicates = by_size_dict.get(file_size)
                if duplicates:
                    duplicates.append(file_path)
                else:
                    by_size_dict[file_size] = [file_path]

    return by_size_dict


# hash a file using the chunk size and an optional limit on the number of chunks to hash
def get_file_hash(file, chunk_size=1024, hash_type=hashlib.sha1, chunk_limit=None):
    hash_func = hash_type()

    with open(file, 'rb') as f:
        if chunk_limit:

                for _ in range(0, chunk_limit):
                    chunk = f.read(chunk_size)
                    hash_func.update(chunk)
        else:
            for chunk in iter(lambda: f.read(chunk_size), b''):
                hash_func.update(chunk)

    file_hash = hash_func.digest()
    return file_hash


# create a list of mappings, mapping files by first chunk to their paths
def make_by_first_chunk_list(by_size_dict, chunk_size, hash_type):
    by_first_chunk_list = []
    for _, files in by_size_dict.items():
        by_first_chunk_dict = {}
        if len(files) >= 2:
            for file in files:
                file_hash = get_file_hash(file, chunk_size, hash_type, 1)

                duplicates = by_first_chunk_dict.get(file_hash)
                if duplicates:
                    duplicates.append(file)
                else:
                    by_first_chunk_dict[file_hash] = [file]

        by_first_chunk_list.append(by_first_chunk_dict)
    return by_first_chunk_list


# create a list of mappings, mapping files by their full hash to their paths
def make_duplicates_list(by_first_chunk_list, chunk_size, hash_type):
    duplicates_list = []
    for dict in by_first_chunk_list:
        duplicates_dict = {}
        for _, files in dict.items():
            if len(files) >= 2:
                for file in files:
                    file_hash = get_file_hash(file, chunk_size, hash_type)

                    duplicates = duplicates_dict.get(file_hash)
                    if duplicates:
                        duplicates.append(file)
                    else:
                        duplicates_dict[file_hash] = [file]

        duplicates_list.append(duplicates_dict)

    return duplicates_list


# print the actual duplicates
def output_duplicates(duplicates_list):
    duplicate_group_num = 1
    for dict in duplicates_list:
        for _, files in dict.items():
            print("Duplicate files group #%d. These files are duplicates:" % duplicate_group_num)
            for file in files:
                print(file)
            print("")
            duplicate_group_num += 1


def check_duplicate_files(root, chunk_size, hash_type):
    # Create a dictionary mapping file sizes to file paths by traversing all files from the root.
    # File paths with similar sizes are stored in a list in the same bucket.
    by_size_dict = make_by_size_dict(root)

    # For each collection of similar sized files, create a hash from each of their first
    # chunks and map these hashes to their paths.
    # File paths with similar first chunk hashes are stored in a list in the same bucket.
    by_first_chunk_list = make_by_first_chunk_list(by_size_dict, chunk_size, hash_type)
    del by_size_dict
    # For each collection of similar first chunk hashed files, create a full hash for each file,
    # and map these hashes to their paths
    # File paths with similar full hashes are stored in a list in the same bucket.
    duplicates_list = make_duplicates_list(by_first_chunk_list, chunk_size, hash_type)
    del by_first_chunk_list
    # Iterate over all buckets and output the similar file paths.
    output_duplicates(duplicates_list)


# constants
CHUNK_SIZE = 1024
HASH_TYPE = hashlib.sha1

# script entry point
if sys.argv[1:]:
    logging.basicConfig(format='%(message)s')

    root_path = sys.argv[1:]
    check_duplicate_files(root_path, CHUNK_SIZE, HASH_TYPE)
else:
    print("Please provide a root path to check")
