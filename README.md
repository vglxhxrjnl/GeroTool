### For Non-Coders

This script is like a handy robot that automates three big tasks for you: downloading videos from the internet, uploading files to online storage, and keeping a neat record of everything on a web page. Here’s what it does in simple terms:

1. **Downloading Videos:**
   - You give it a text file with a list of web addresses (URLs) where videos are located—like links to YouTube or other sites.
   - The script grabs those videos and saves them to a folder on your computer. It names each video file with details like the title, upload date, and a unique video ID, so they’re easy to recognize.
   - If a website needs you to be logged in to download a video (like a private video), the script can use special “cookies” (think of them as digital permission slips) from a folder you set up. It figures out which cookies to use based on the website’s address.

2. **Uploading Files:**
   - Once the videos are downloaded—or if you already have files in the folder—the script takes everything in that folder (and any subfolders) and uploads them to two online storage services: Gofile and Pixeldrain.
   - This gives you two copies of each file online, which is great for backups or sharing with friends.
   - For every file it uploads, the script makes a unique ID (like a random code), notes the date, and saves the web link where you can find the file. It keeps all this info in a file called “upload_log.json” on your computer.

3. **Keeping a Record on a Web Page:**
   - The script also updates a special web page on GitHub called a “Gist.” Think of it as an online notepad.
   - It takes the info from the upload log and adds new entries to a Markdown file (a simple text file with formatting). Each entry shows the unique ID, the date, and the link to the uploaded file.
   - Then, it sends the full Markdown file to the Gist, so you have an up-to-date list online. If an upload’s details are already there, it won’t add them again—it’s smart like that!

**How to Use It:**
- You need to set up a file called `.env` with some secret codes (like passwords) for Gofile, Pixeldrain, and GitHub, plus tell it where your folders are.
- Run the script by typing a command like `python combined_script.py my_urls.txt` in your computer’s terminal, where `my_urls.txt` is your list of video links.
- The script checks if everything’s set up right (like making sure the cookies folder exists) and stops if something’s missing, so you know what to fix.

In short, this script saves you tons of time by handling video downloads, uploads, and record-keeping all in one go, keeping everything organized and accessible.

---

### For Those Who Know About Code

This Python script automates downloading videos from URLs, uploading files to Gofile and Pixeldrain, and updating a GitHub Gist with upload details. It’s modular, uses environment variables for configuration, and includes error handling for robustness. Below is a detailed breakdown.

#### Key Features

- **Environment Setup:**
  - Loads configuration from a `.env` file using `dotenv`, including API tokens (`GOFILE_TOKEN`, `PIXELDRAIN_API_KEY`, `GITHUB_TOKEN`), folder paths (`FOLDER`, `COOKIES_FOLDER`), and Gist details (`GIST_ID`, `MD_FILE`).
  - Validates all required environment variables and ensures `COOKIES_FOLDER` is a valid directory, exiting with an error if not.

- **Video Downloading:**
  - Uses `yt_dlp` to download videos from URLs listed in a file provided as a command-line argument.
  - Saves files to a specified folder with a template: `[title][upload_date]_id.ext`.
  - Supports cookies for authenticated downloads by matching domain-specific cookie files (e.g., `youtube.com_cookies.txt`) from `COOKIES_FOLDER`.

- **File Uploading:**
  - Recursively uploads all files from the specified folder to Gofile and Pixeldrain using their APIs.
  - Generates a unique 10-character ID for each upload with `generate_random_id`.
  - Logs each upload in `upload_log.json` with the ID, date, service name, and download URL.
  - Shows progress with a `tqdm` progress bar.

- **Gist Updating:**
  - Reads `upload_log.json`, checks for new entries by comparing IDs with those in an existing Markdown file (`MD_FILE`), and appends new entries in the format: `#### ID: {id} - {date}\n\nURL: {link}`.
  - Updates a GitHub Gist with the full Markdown content via a PATCH request to the GitHub API, using `GITHUB_TOKEN` for authentication.

#### Function Breakdown

- **Utility Functions:**
  - **`generate_random_id(length=10)`**: Returns a random string of letters and digits.
  - **`get_files_recursive(folder_path)`**: Uses `pathlib` to list all files in a folder and its subfolders recursively.

- **Download and Upload Functions:**
  - **`get_gofile_server()`**: Queries the Gofile API for an upload server name.
  - **`upload_to_gofile(file_path)`**: Uploads a file to Gofile with the token, returning the download page URL.
  - **`upload_to_pixeldrain(file_path)`**: Uploads a file to Pixeldrain with Basic Auth, returning the download URL.
  - **`append_to_log(entry)`**: Appends a JSON object to `upload_log.json`, handling file creation and errors.
  - **`download_videos(url_file, folder)`**: Downloads videos with `yt_dlp`, using cookies if available.
  - **`upload_files(folder_path)`**: Uploads all files to both services, logging each success.

- **Gist Update Function:**
  - **`update_gist(json_file, md_file, gist_id, github_token)`**: Processes the log, updates the Markdown file, and patches the Gist.

- **Main Function:**
  - **`main()`**: Takes a URL file as `sys.argv[1]`, runs `download_videos`, `upload_files`, and `update_gist` in sequence.

#### Technical Details

- **Dependencies:** `sys`, `os`, `json`, `random`, `string`, `base64`, `datetime`, `pathlib`, `requests`, `dotenv`, `tqdm`, `yt_dlp`, `urllib.parse`.
- **Error Handling:** Checks for file existence, valid JSON, API response status, and network errors, printing descriptive messages.
- **Execution:** Run with `python combined_script.py <url_list.txt>`.

This script is a powerful tool for automating video and file management workflows, with a clean structure that’s easy to extend or debug.

#### [VIETNAMESE-README](____/README-VN.md)
