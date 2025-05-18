#!/usr/bin/python3
import sys
import os
import json
import random
import string
import base64
from datetime import datetime
from pathlib import Path
import requests
from dotenv import load_dotenv
from tqdm import tqdm
import yt_dlp
from urllib.parse import urlparse

# Load environment variables from .env file
load_dotenv()

# Check for required environment variables
required_keys = ["GOFILE_TOKEN", "PIXELDRAIN_API_KEY", "GITHUB_TOKEN", "FOLDER", "GIST_ID", "MD_FILE", "COOKIES_FOLDER"]
for key in required_keys:
    if not os.getenv(key):
        print(f"Error: {key} not specified in .env file.")
        sys.exit(1)

# Validate COOKIES_FOLDER
cookies_folder = os.getenv('COOKIES_FOLDER')
if not os.path.isdir(cookies_folder):
    print(f"Error: COOKIES_FOLDER '{cookies_folder}' is not a valid directory.")
    sys.exit(1)

# Define the log file name
LOG_FILE = "upload_log.json"

### Utility Functions

def generate_random_id(length=10):
    """Generate a random string of letters and digits."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def get_files_recursive(folder_path):
    """Get all files in the folder and its subfolders recursively."""
    folder = Path(folder_path)
    if not folder.is_dir():
        print(f"Error: {folder_path} is not a valid directory.")
        sys.exit(1)
    return [f for f in folder.rglob("*") if f.is_file()]

### Download and Upload Functions

def get_gofile_server():
    """Get a server from Gofile API."""
    url = "https://api.gofile.io/servers"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "ok" and "servers" in data.get("data", {}):
            servers = data["data"]["servers"]
            if servers:
                return servers[0]["name"]
            else:
                print("Error: No servers available from Gofile API.")
                return None
        else:
            print(f"Error getting Gofile server: {data.get('message', 'Unknown error')}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Gofile server: {str(e)}")
        return None
    except ValueError as e:
        print(f"Error decoding Gofile server response: {str(e)}")
        return None

def upload_to_gofile(file_path):
    """Upload a file to Gofile using direct API calls."""
    server = get_gofile_server()
    if not server:
        return None
    url = f"https://{server}.gofile.io/uploadFile"
    try:
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f)}
            headers = {"Authorization": f"Bearer {os.getenv('GOFILE_TOKEN')}"}
            response = requests.post(url, files=files, headers=headers)
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "ok":
                return data["data"]["downloadPage"]
            else:
                print(f"Error uploading {file_path} to Gofile: {data.get('message', 'Unknown error')}")
                return None
    except requests.exceptions.RequestException as e:
        print(f"Error uploading {file_path} to Gofile: {str(e)}")
        return None
    except ValueError as e:
        print(f"Error decoding Gofile upload response: {str(e)}")
        return None

def upload_to_pixeldrain(file_path):
    """Upload a file to Pixeldrain and return the download URL."""
    url = "https://pixeldrain.com/api/file"
    try:
        with open(file_path, "rb") as f:
            auth_string = f":{os.getenv('PIXELDRAIN_API_KEY')}".encode("utf-8")
            auth_header = f"Basic {base64.b64encode(auth_string).decode('utf-8')}"
            files = {"file": (file_path.name, f)}
            headers = {"Authorization": auth_header}
            response = requests.post(url, files=files, headers=headers)
            response.raise_for_status()
            data = response.json()
            if data.get("success"):
                file_id = data["id"]
                return f"https://pixeldrain.com/u/{file_id}"
            else:
                print(f"Error uploading {file_path} to Pixeldrain: {data.get('message', 'Unknown error')}")
                return None
    except requests.exceptions.RequestException as e:
        print(f"Error uploading {file_path} to Pixeldrain: {str(e)}")
        return None
    except ValueError as e:
        print(f"Error decoding Pixeldrain response: {str(e)}")
        return None

def append_to_log(entry):
    """Append an entry to the JSON log file."""
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                try:
                    data = json.load(f)
                    if not isinstance(data, list):
                        data = []
                except json.JSONDecodeError:
                    data = []
        else:
            data = []
        data.append(entry)
        with open(LOG_FILE, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Updated log file: {LOG_FILE}")
    except Exception as e:
        print(f"Error writing to log file: {str(e)}")

def download_videos(url_file, folder):
    """Download videos from URLs in the given file using yt-dlp to the specified folder."""
    if not os.path.exists(url_file):
        print(f"Error: File '{url_file}' not found.")
        sys.exit(1)
    with open(url_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    if not urls:
        print("No URLs found in the file.")
        sys.exit(1)
    os.makedirs(folder, exist_ok=True)
    outtmpl = os.path.join(folder, '[%(title)s][%(upload_date)s]_%(id)s.%(ext)s')
    cookies_folder = os.getenv('COOKIES_FOLDER')
    for url in urls:
        netloc = urlparse(url).netloc
        if not netloc:
            print(f"Invalid URL: {url}")
            continue
        cookies_file = os.path.join(cookies_folder, f"{netloc}_cookies.txt")
        if os.path.exists(cookies_file):
            ydl_opts = {
                'outtmpl': outtmpl,
                'format': 'best',
                'cookiefile': cookies_file,
            }
            print(f"Using cookies file for {url}: {cookies_file}")
        else:
            ydl_opts = {
                'outtmpl': outtmpl,
                'format': 'best',
            }
            print(f"No cookies file found for {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

def upload_files(folder_path):
    """Upload all files from the folder to Gofile and Pixeldrain."""
    files = get_files_recursive(folder_path)
    if not files:
        print("No files found in the specified directory.")
        return
    print(f"Found {len(files)} files to upload.")
    for file_path in tqdm(files, desc="Uploading files", unit="file"):
        file_path = Path(file_path)
        current_date = datetime.now().strftime("%Y-%m-%d")
        # Upload to Gofile
        gofile_url = upload_to_gofile(file_path)
        if gofile_url:
            entry = {
                "ID": generate_random_id(),
                "Details": {
                    "Dates": current_date,
                    "Services": "gofile.io",
                    "Link": gofile_url
                }
            }
            append_to_log(entry)
            print(f"Uploaded {file_path.name} to Gofile: {gofile_url}")
        # Upload to Pixeldrain
        pixeldrain_url = upload_to_pixeldrain(file_path)
        if pixeldrain_url:
            entry = {
                "ID": generate_random_id(),
                "Details": {
                    "Dates": current_date,
                    "Services": "pixeldrain.com",
                    "Link": pixeldrain_url
                }
            }
            append_to_log(entry)
            print(f"Uploaded {file_path.name} to Pixeldrain: {pixeldrain_url}")

### Gist Update Function

def update_gist(json_file, md_file, gist_id, github_token):
    """Process JSON log and update GitHub Gist with Markdown content."""
    # Read existing Markdown content to avoid duplicates
    if os.path.exists(md_file):
        with open(md_file, "r") as f:
            existing_content = f.read()
        # Extract existing IDs
        existing_ids = set()
        for line in existing_content.splitlines():
            if line.startswith("#### ID:"):
                parts = line.split(" - ")
                if len(parts) >= 1:
                    id_part = parts[0].replace("#### ID:", "").strip()
                    existing_ids.add(id_part)
    else:
        existing_content = ""
        existing_ids = set()

    # Read JSON log
    try:
        with open(json_file, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: JSON file {json_file} not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {json_file}.")
        return

    # Process new entries
    new_entries = []
    for obj in data:
        id = obj["ID"]
        if id not in existing_ids:
            date = obj["Details"]["Dates"]
            link = obj["Details"]["Link"]
            formatted_entry = f"#### ID: {id} - {date}\n\nURL: `{link}`\n"
            new_entries.append(formatted_entry)
            existing_ids.add(id)

    # Append new entries to Markdown file
    if new_entries:
        separator = "\n---\n" if existing_content else ""
        new_content = separator + "\n---\n".join(new_entries)
        with open(md_file, "a") as f:
            f.write(new_content)
        print(f"Appended {len(new_entries)} new entries to {md_file}")
    else:
        print("No new entries to append.")

    # Update Gist with the full Markdown content
    with open(md_file, "r") as f:
        full_content = f.read()

    url = f"https://api.github.com/gists/{gist_id}"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    data = {
        "files": {
            md_file: {
                "content": full_content
            }
        }
    }

    try:
        response = requests.patch(url, headers=headers, json=data)
        if response.status_code == 200:
            print("Gist updated successfully.")
        else:
            print(f"Failed to update Gist: {response.status_code}")
            print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error updating Gist: {e}")

### Main Execution

def main():
    """Main function to execute download, upload, and Gist update."""
    if len(sys.argv) != 2:
        print("Usage: python combined_script.py <url_list.txt>")
        sys.exit(1)

    url_file = sys.argv[1]
    folder = os.getenv("FOLDER")
    md_file = os.getenv("MD_FILE")
    gist_id = os.getenv("GIST_ID")
    github_token = os.getenv("GITHUB_TOKEN")

    # Execute downandup: Download and upload
    download_videos(url_file, folder)
    upload_files(folder)

    # Execute maingist: Update Gist
    update_gist(LOG_FILE, md_file, gist_id, github_token)

if __name__ == "__main__":
    main()
