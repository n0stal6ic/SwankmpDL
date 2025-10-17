import requests
import os
import xml.etree.ElementTree as ET

def download_file(url, output_file, chunk_size=10 * 1024 * 1024):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "*/*",
        "Accept-Encoding": "identity",
        "Connection": "keep-alive",
    }
    r = requests.head(url, headers=headers)
    file_size = int(r.headers.get("Content-Length", 0))
    print(f"\nDownloading {os.path.basename(output_file)} ({file_size} bytes)")
    with open(output_file, "wb") as f:
        for start in range(0, file_size, chunk_size):
            end = min(start + chunk_size - 1, file_size - 1)
            headers["Range"] = f"bytes={start}-{end}"
            r = requests.get(url, headers=headers, stream=True)
            if r.status_code in (200, 206):
                f.write(r.content)
                print(f"Chunk {start}-{end} written")
            else:
                print(f"Error: HTTP {r.status_code}")
                break
    print(f"Downloaded: {output_file}")
def main():
    try:
        print("=== Drag & Drop MPD file. ===")
        mpd_file = input("MPD path: ").strip('"')
        if not os.path.isfile(mpd_file):
            print("File not found.")
            input("Press Enter to exit...")
            return
        tree = ET.parse(mpd_file)
        root = tree.getroot()
        ns = {"mpd": "urn:mpeg:dash:schema:mpd:2011"}
        base_url = input(
            "Enter the base URL up to the media files (ending with '/'): "
        ).strip()
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        output_folder = os.path.join(desktop, "swankmp")
        os.makedirs(output_folder, exist_ok=True)
        print(f"\nFiles: {output_folder}")
        video_reps = root.findall(".//mpd:AdaptationSet[@mimeType='video/mp4']/mpd:Representation", ns)
        best_video = max(video_reps, key=lambda x: int(x.attrib.get("bandwidth", 0)))
        video_path = best_video.find("mpd:BaseURL", ns).text.strip()
        video_url = base_url + video_path
        video_output = os.path.join(output_folder, "video.mp4")
        audio_rep = root.find(".//mpd:AdaptationSet[@mimeType='audio/mp4']/mpd:Representation", ns)
        audio_path = audio_rep.find("mpd:BaseURL", ns).text.strip()
        audio_url = base_url + audio_path
        audio_output = os.path.join(output_folder, "audio.mp4")
        vtt_rep = root.find(".//mpd:AdaptationSet[@mimeType='text/vtt']/mpd:Representation/mpd:BaseURL", ns)
        vtt_url = base_url + vtt_rep.text.strip() if vtt_rep is not None else None
        vtt_output = os.path.join(output_folder, os.path.basename(vtt_rep.text)) if vtt_rep is not None else None
        print("\n=== Downloading ===")
        if os.path.exists(video_output):
            print("Skipping video.mp4 (already exists)")
        else:
            download_file(video_url, video_output)
        if os.path.exists(audio_output):
            print("Skipping audio.mp4 (already exists)")
        else:
            download_file(audio_url, audio_output)
        if vtt_url:
            if os.path.exists(vtt_output):
                print(f"Skipping {os.path.basename(vtt_output)} (already exists)")
            else:
                print(f"\nDownloading subtitle: {os.path.basename(vtt_output)}")
                r = requests.get(vtt_url, headers={"User-Agent": "Mozilla/5.0"})
                if r.status_code == 200:
                    with open(vtt_output, "wb") as f:
                        f.write(r.content)
                    print(f"Subtitle downloaded: {vtt_output}")
                else:
                    print(f"Failed to download subtitle (status {r.status_code})")
        else:
            print("No subtitle in MPD")

        print("\nDownloads complete.")
    except Exception as e:
        print(f"\nError: {e}")
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
