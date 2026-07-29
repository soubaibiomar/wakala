import os
import logging
from typing import List
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from models.listing import Listing

logger = logging.getLogger(__name__)

class ImageDownloader:
    def __init__(self, base_dir: str = "images"):
        self.base_dir = base_dir
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
            
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        })

    def download_gallery(self, listing: Listing) -> List[str]:
        """
        Downloads all images in a listing to images/<source_site>/<listing_id>/<n>.jpg.
        Skips already downloaded images.
        Returns a list of local file paths.
        """
        if not listing.images:
            return []
            
        listing_dir = os.path.join(self.base_dir, listing.source_site, listing.listing_id)
        if not os.path.exists(listing_dir):
            os.makedirs(listing_dir)
            
        local_paths = []
        for i, img_url in enumerate(listing.images):
            # Try to get extension from URL, fallback to .jpg
            ext = ".jpg"
            if "." in img_url.split("/")[-1]:
                # Very basic extension extraction (avoids query params)
                possible_ext = img_url.split("/")[-1].split("?")[0].split(".")[-1]
                if possible_ext.lower() in ["jpg", "jpeg", "png", "webp"]:
                    ext = f".{possible_ext}"
            
            local_filename = f"{i}{ext}"
            local_filepath = os.path.join(listing_dir, local_filename)
            
            if os.path.exists(local_filepath) and os.path.getsize(local_filepath) > 0:
                local_paths.append(local_filepath)
                continue
                
            try:
                resp = self.session.get(img_url, timeout=10)
                if resp.status_code == 200:
                    with open(local_filepath, "wb") as f:
                        f.write(resp.content)
                    local_paths.append(local_filepath)
                else:
                    logger.warning(f"Failed to download image {img_url} for listing {listing.listing_id}: Status {resp.status_code}")
            except Exception as e:
                logger.error(f"Error downloading image {img_url}: {e}")
                
        return local_paths
