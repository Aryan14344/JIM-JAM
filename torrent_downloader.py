from qbittorrent import Client
import time
import os
from config import TARGET_SUBREDDITS

class TorrentManager:
    """
    Principal Architect module for programmatically managing 
    large-scale archival downloads via qBittorrent WebUI.
    """
    def __init__(self, host="http://127.0.0.1:8080/", username="admin", password="123456"):
        try:
            self.qb = Client(host)
            self.qb.login(username, password)
            print("[*] Successfully connected to qBittorrent WebUI.")
        except Exception as e:
            print(f"[!] Connection failed: {e}")
            print("[!] Ensure qBittorrent is running, WebUI is enabled at http://127.0.0.1:8080/, and credentials are correct.")
            self.qb = None

    def pause_torrent(self, info_hash):
        """Safely pause the torrent, handling API changes in qBittorrent 4.5.0+"""
        try:
            self.qb.pause(info_hash)
        except Exception as e:
            if "404" in str(e):
                self.qb._post('torrents/stop', data={'hashes': info_hash.lower()})
            else:
                raise e

    def resume_torrent(self, info_hash):
        """Safely resume the torrent, handling API changes in qBittorrent 4.5.0+"""
        try:
            self.qb.resume(info_hash)
        except Exception as e:
            if "404" in str(e):
                self.qb._post('torrents/start', data={'hashes': info_hash.lower()})
            else:
                raise e

    def download_subreddits(self, magnet_link, subreddit_list, download_path="data"):
        if not self.qb:
            return

        # Ensure download path is absolute
        abs_path = os.path.abspath(download_path)
        if not os.path.exists(abs_path):
            os.makedirs(abs_path)

        print("[*] Adding magnet link to qBittorrent...")
        self.qb.download_from_link(magnet_link, savepath=abs_path)
        
        info_hash = "3e3f64dee22dc304cdd2546254ca1f8e8ae542b4"
        
        print("[*] Waiting for metadata to resolve...")
        while True:
            torrents = self.qb.torrents()
            target = next((t for t in torrents if t['hash'].lower() == info_hash.lower()), None)
            if target and target['state'] != 'metaDL':
                break
            time.sleep(5)

        print("[*] Metadata resolved. Pausing torrent while applying file priorities...")
        self.pause_torrent(info_hash)
        
        files = self.qb.get_torrent_files(info_hash)
        
        target_map = {f"{sub.lower()}_comments.zst": sub for sub in subreddit_list}
        found_subs = []
        
        wanted_indices = []
        unwanted_indices = []

        # Analyze all ~80,000 files
        for index, f in enumerate(files):
            # Extract filename and convert to lowercase for comparison
            file_name_actual = f['name'].replace('\\', '/').split('/')[-1]
            file_name_lower = file_name_actual.lower()
            
            if file_name_lower in target_map:
                wanted_indices.append(str(index))
                found_subs.append(target_map[file_name_lower])
            else:
                unwanted_indices.append(str(index))

        # Helper function to send requests in batches 
        def set_priorities_in_chunks(indices, priority):
            chunk_size = 500  # Process in chunks of 500
            total_chunks = (len(indices) + chunk_size - 1) // chunk_size
            
            for i in range(0, len(indices), chunk_size):
                chunk = "|".join(indices[i:i+chunk_size])
                
                # BYPASS: Directly calling the underlying API endpoint to avoid the wrapper's integer type-checking
                self.qb._post('torrents/filePrio', data={
                    'hash': info_hash.lower(),
                    'id': chunk,
                    'priority': priority
                })
                print(f"    -> Processed chunk {i//chunk_size + 1}/{total_chunks}...")

        print(f"[*] Total files found: {len(files)}. Setting priorities...")
        
        # 1. Unselect unwanted files first (Priority 0 = Do not download)
        if unwanted_indices:
            print(f"[*] Unselecting {len(unwanted_indices)} unwanted files to save bandwidth...")
            set_priorities_in_chunks(unwanted_indices, priority=0)
        
        # 2. Select only the target subreddits (Priority 1 = Normal)
        if wanted_indices:
            print(f"[*] Selecting {len(wanted_indices)} target subreddits...")
            set_priorities_in_chunks(wanted_indices, priority=1)
            
            missing = set(subreddit_list) - set(found_subs)
            if missing:
                print(f"[!] Missing subreddits (not in dump): {list(missing)[:10]}...")
        else:
            print("[!] No matching subreddits found in the torrent.")

        print("[*] Resuming torrent with only the selected files...")
        self.resume_torrent(info_hash)
        print("[*] Done! Target files are now downloading.")


if __name__ == "__main__":
    MAGNET = "magnet:?xt=urn:btih:3e3f64dee22dc304cdd2546254ca1f8e8ae542b4&tr=https%3A%2F%2Facademictorrents.com%2Fannounce.php&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce"
    
    manager = TorrentManager()
    manager.download_subreddits(MAGNET, subreddit_list=TARGET_SUBREDDITS)