import os
import json
import time
import requests
from pathlib import Path
from publish_reels import (
    ACCESS_TOKEN, 
    IG_BUSINESS_ACCOUNT_ID, 
    API_VERSION, 
    BASE_URL, 
    check_status, 
    _instagram_resumable_upload
)

def publish_instagram_carousel_local(image_paths, caption):
    """
    Publishes a Carousel to Instagram using local image files.
    Each image is uploaded via Resumable Binary Upload.
    """
    if not IG_BUSINESS_ACCOUNT_ID:
        print("[!] IG_BUSINESS_ACCOUNT_ID missing. Skipping Instagram Carousel.")
        return

    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    child_ids = []

    print(f"[*] Starting binary upload for {len(image_paths)} carousel items...")

    for path in image_paths:
        if not os.path.exists(path):
            print(f"[-] File not found: {path}")
            continue
        
        file_size = os.path.getsize(path)
        
        # Step 1: Create media container for this item
        url = f"{BASE_URL}/{API_VERSION}/{IG_BUSINESS_ACCOUNT_ID}/media"
        payload = {
            "is_carousel_item": "true",
            "upload_type": "resumable"
        }
        
        try:
            response = requests.post(url, headers=headers, data=payload).json()
            container_id = response.get("id")
            
            if not container_id:
                print(f"[-] Failed to create item container for {path}: {response}")
                continue

            # Step 2: Upload binary data
            if _instagram_resumable_upload(path, file_size, container_id):
                # Step 3: Wait for processing
                if check_status(container_id, "instagram"):
                    child_ids.append(container_id)
                    print(f"    [+] Item ready: {container_id}")
                else:
                    print(f"    [-] Item processing failed: {container_id}")
            else:
                print(f"    [-] Binary upload failed for: {path}")
        except Exception as e:
            print(f"[-] Error uploading {path}: {e}")

    if not child_ids:
        print("[-] No items were successfully uploaded. Aborting carousel.")
        return

    # Step 4: Create the main CAROUSEL container
    print("[*] Initializing main Carousel container...")
    carousel_payload = {
        "media_type": "CAROUSEL",
        "caption": caption,
        "children": ",".join(child_ids)
    }
    carousel_url = f"{BASE_URL}/{API_VERSION}/{IG_BUSINESS_ACCOUNT_ID}/media"
    try:
        res = requests.post(carousel_url, headers=headers, data=carousel_payload).json()
        carousel_container_id = res.get("id")

        if not carousel_container_id:
            print(f"[-] Failed to create Carousel container: {res}")
            return

        # Step 5: Final Poll and Publish
        if check_status(carousel_container_id, "instagram"):
            print("[*] Publishing Instagram Carousel...")
            publish_url = f"{BASE_URL}/{API_VERSION}/{IG_BUSINESS_ACCOUNT_ID}/media_publish"
            publish_payload = {"creation_id": carousel_container_id}
            res = requests.post(publish_url, headers=headers, data=publish_payload).json()
            print(f"[+] Instagram Carousel Response: {res}")
            return res
    except Exception as e:
        print(f"[-] Error during final carousel publication: {e}")

    return None

def publish_facebook_carousel_local(image_paths, caption):
    """
    Publishes a Carousel to a Facebook Page using local image files.
    """
    from publish_reels import get_page_access_token, FB_PAGE_ID
    if not FB_PAGE_ID:
        print("[!] FB_PAGE_ID missing. Skipping Facebook Carousel.")
        return

    page_token = get_page_access_token(FB_PAGE_ID)
    headers = {"Authorization": f"Bearer {page_token}"}
    
    attached_media = []
    print(f"[*] Uploading {len(image_paths)} images to Facebook Page...")

    for path in image_paths:
        if not os.path.exists(path):
            continue
        
        # Step 1: Upload photo as unpublished
        url = f"{BASE_URL}/{API_VERSION}/{FB_PAGE_ID}/photos"
        files = {
            "source": open(path, "rb")
        }
        payload = {
            "published": "false",
            "access_token": page_token
        }
        
        try:
            res = requests.post(url, data=payload, files=files).json()
            photo_id = res.get("id")
            if photo_id:
                attached_media.append({"media_fbid": photo_id})
                print(f"    [+] Uploaded photo: {photo_id}")
            else:
                print(f"    [-] Failed to upload photo {path}: {res}")
        except Exception as e:
            print(f"[-] Error uploading {path} to Facebook: {e}")

    if not attached_media:
        print("[-] No photos were uploaded to Facebook. Aborting.")
        return

    # Step 2: Create post with attached media
    print("[*] Creating Facebook Carousel post...")
    post_url = f"{BASE_URL}/{API_VERSION}/{FB_PAGE_ID}/feed"
    post_payload = {
        "message": caption,
        "attached_media": json.dumps(attached_media),
        "access_token": page_token
    }
    
    try:
        res = requests.post(post_url, data=post_payload).json()
        print(f"[+] Facebook Post Response: {res}")
        return res
    except Exception as e:
        print(f"[-] Error creating Facebook post: {e}")
        return None

def publish_threads_carousel(image_urls, caption):
    """
    Publishes a Carousel to Threads.
    image_urls: List of publicly accessible image URLs.
    """
    from publish_reels import THREADS_USER_ID, THREADS_BASE_URL, THREAD_TOKEN, ACCESS_TOKEN, check_status
    
    if not THREADS_USER_ID:
        print("[!] THREADS_USER_ID missing. Skipping Threads Carousel.")
        return

    current_token = THREAD_TOKEN or ACCESS_TOKEN
    headers = {"Authorization": f"Bearer {current_token}"}
    params = {"access_token": current_token}
    
    # Step 1: Create individual item containers
    child_ids = []
    print(f"[*] Creating {len(image_urls)} Threads carousel item containers...")
    for url in image_urls:
        payload = {
            "media_type": "IMAGE",
            "image_url": url,
            "is_carousel_item": "true"
        }
        create_url = f"{THREADS_BASE_URL}/v1.0/me/threads"
        try:
            res = requests.post(create_url, params=params, data=payload).json()
            item_id = res.get("id")
            if item_id:
                # Wait for item to be ready
                if check_status(item_id, "threads", token=current_token):
                    child_ids.append(item_id)
                    print(f"    [+] Created Threads item: {item_id}")
                else:
                    print(f"    [-] Threads item failed: {item_id}")
            else:
                print(f"    [-] Failed to create Threads item for {url}: {res}")
        except Exception as e:
            print(f"[-] Error uploading {url} to Threads: {e}")

    if not child_ids:
        print("[-] No items were created on Threads. Aborting.")
        return

    # Step 2: Create the main CAROUSEL container
    print("[*] Initializing Threads Carousel container...")
    
    # Threads has a strict 500 character limit for the 'text' parameter
    safe_caption = (caption or "")[:500]
    
    carousel_payload = {
        "media_type": "CAROUSEL",
        "text": safe_caption,
        "children": ",".join(child_ids)
    }
    carousel_url = f"{THREADS_BASE_URL}/v1.0/me/threads"
    try:
        res = requests.post(carousel_url, params=params, data=carousel_payload).json()
        carousel_container_id = res.get("id")

        if not carousel_container_id:
            print(f"[-] Failed to create Threads Carousel container: {res}")
            return

        # Step 3: Poll and Publish
        if check_status(carousel_container_id, "threads", token=current_token):
            print("[*] Publishing Threads Carousel...")
            publish_url = f"{THREADS_BASE_URL}/v1.0/me/threads_publish"
            publish_payload = {
                "creation_id": carousel_container_id,
                "access_token": current_token
            }
            res = requests.post(publish_url, data=publish_payload).json()
            print(f"[+] Threads Response: {res}")
            return res
    except Exception as e:
        print(f"[-] Error during final Threads publication: {e}")

    return None


# ════════════════════════════════════════════════════════════════
#  SINGLE IMAGE POSTS
# ════════════════════════════════════════════════════════════════

def publish_single_image_instagram(image_path, caption):
    """Publish a single image post to Instagram via local binary upload."""
    if not IG_BUSINESS_ACCOUNT_ID:
        print("[!] IG_BUSINESS_ACCOUNT_ID missing. Skipping Instagram single post.")
        return

    if not os.path.exists(image_path):
        print(f"[-] File not found: {image_path}")
        return

    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    file_size = os.path.getsize(image_path)

    # Step 1: Create media container
    url = f"{BASE_URL}/{API_VERSION}/{IG_BUSINESS_ACCOUNT_ID}/media"
    payload = {
        "caption": caption,
        "upload_type": "resumable"
    }

    try:
        response = requests.post(url, headers=headers, data=payload).json()
        container_id = response.get("id")
        if not container_id:
            print(f"[-] Failed to create container: {response}")
            return

        # Step 2: Upload binary data
        if _instagram_resumable_upload(image_path, file_size, container_id):
            # Step 3: Wait for processing
            if check_status(container_id, "instagram"):
                # Step 4: Publish
                print("[*] Publishing Instagram single image...")
                publish_url = f"{BASE_URL}/{API_VERSION}/{IG_BUSINESS_ACCOUNT_ID}/media_publish"
                publish_payload = {"creation_id": container_id}
                res = requests.post(publish_url, headers=headers, data=publish_payload).json()
                print(f"[+] Instagram Single Image Response: {res}")
                return res
            else:
                print(f"[-] Processing failed: {container_id}")
        else:
            print(f"[-] Binary upload failed for: {image_path}")
    except Exception as e:
        print(f"[-] Error publishing single image to Instagram: {e}")

    return None


def publish_single_image_facebook(image_path, caption):
    """Publish a single image post to a Facebook Page."""
    from publish_reels import get_page_access_token, FB_PAGE_ID
    if not FB_PAGE_ID:
        print("[!] FB_PAGE_ID missing. Skipping Facebook single post.")
        return

    if not os.path.exists(image_path):
        print(f"[-] File not found: {image_path}")
        return

    page_token = get_page_access_token(FB_PAGE_ID)

    url = f"{BASE_URL}/{API_VERSION}/{FB_PAGE_ID}/photos"
    try:
        with open(image_path, "rb") as f:
            files = {"source": f}
            payload = {
                "message": caption,
                "published": "true",
                "access_token": page_token
            }
            res = requests.post(url, data=payload, files=files).json()
            print(f"[+] Facebook Single Image Response: {res}")
            return res
    except Exception as e:
        print(f"[-] Error publishing single image to Facebook: {e}")

    return None


def publish_single_image_threads(image_path, caption):
    """Publish a single image post to Threads (requires public URL or local workaround)."""
    from publish_reels import THREADS_USER_ID, THREADS_BASE_URL, THREAD_TOKEN, ACCESS_TOKEN, check_status

    if not THREADS_USER_ID:
        print("[!] THREADS_USER_ID missing. Skipping Threads single post.")
        return

    current_token = THREAD_TOKEN or ACCESS_TOKEN
    params = {"access_token": current_token}

    # Threads requires a public URL for images
    # For now, we skip if not accessible via CDN
    # This will be handled by GitHub Action post-CDN step
    print("[!] Threads single image requires public URL. Skipping local publish.")
    print("    (Will be published via CDN workflow)")

    return None


def publish_threads_single(image_url, caption):
    """
    Publishes a single image to Threads.
    image_url: Publicly accessible image URL.
    """
    from publish_reels import THREADS_USER_ID, THREADS_BASE_URL, THREAD_TOKEN, ACCESS_TOKEN, check_status
    
    if not THREADS_USER_ID:
        print("[!] THREADS_USER_ID missing. Skipping Threads single post.")
        return

    current_token = THREAD_TOKEN or ACCESS_TOKEN
    params = {"access_token": current_token}
    
    # Threads has a strict 500 character limit
    safe_caption = (caption or "")[:500]
    
    payload = {
        "media_type": "IMAGE",
        "image_url": image_url,
        "text": safe_caption
    }
    
    create_url = f"{THREADS_BASE_URL}/v1.0/me/threads"
    try:
        res = requests.post(create_url, params=params, data=payload).json()
        container_id = res.get("id")
        
        if not container_id:
            print(f"[-] Failed to create Threads container: {res}")
            return

        if check_status(container_id, "threads", token=current_token):
            print("[*] Publishing Threads single post...")
            publish_url = f"{THREADS_BASE_URL}/v1.0/me/threads_publish"
            publish_payload = {
                "creation_id": container_id,
                "access_token": current_token
            }
            res = requests.post(publish_url, data=publish_payload).json()
            print(f"[+] Threads Single Post Response: {res}")
            return res
    except Exception as e:
        print(f"[-] Error during Threads single publication: {e}")

    return None
