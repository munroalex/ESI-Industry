"""
Module to download and extract the latest EVE Online Static Data Export (SDE) from Fuzzwork.
"""
import os
import bz2
import requests

# URL and filenames
SDE_URL = "https://www.fuzzwork.co.uk/dump/sqlite-latest.sqlite.bz2"
MD5_URL = "https://www.fuzzwork.co.uk/dump/sqlite-latest.sqlite.bz2.md5"
LOCAL_FILE = "sqlite-latest.sqlite.bz2"
EXTRACTED_FILE = "sqlite-latest.sqlite"
MD5_FILE = "sqlite-latest.md5"

def get_remote_md5():
    """Gets the MD5 checksum of the remote SDE file."""
    response = requests.get(MD5_URL, timeout=10)
    if response.status_code == 200:
        return response.text.strip()
    return None

def get_local_md5():
    """Reads the stored MD5 checksum of the last downloaded SDE file."""
    if os.path.exists(MD5_FILE):
        with open(MD5_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None

def save_local_md5(md5_hash):
    """Saves the MD5 checksum of the last downloaded SDE file."""
    with open(MD5_FILE, "w", encoding="utf-8") as f:
        f.write(md5_hash)

def download_sde():
    """Downloads the SDE file if the remote MD5 has changed."""
    remote_md5 = get_remote_md5()
    local_md5 = get_local_md5()

    if os.path.exists(EXTRACTED_FILE) and remote_md5 and local_md5 == remote_md5:
        print("SDE is up to date. No need to download.")
        return

    print("Downloading SDE...")
    response = requests.get(SDE_URL, stream=True, timeout=10)
    if response.status_code == 200:
        with open(LOCAL_FILE, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print("Download complete.")
        extract_sde()
        save_local_md5(remote_md5)
    else:
        print("Failed to download SDE. HTTP Status Code:", response.status_code)

def extract_sde():
    """Extracts the downloaded SDE file."""
    print("Extracting SDE...")
    with bz2.BZ2File(LOCAL_FILE, "rb") as source, open(EXTRACTED_FILE, "wb") as dest:
        dest.write(source.read())
    print("Extraction complete.")

def main():
    """Main entry point of the script."""
    download_sde()

if __name__ == "__main__":
    main()
