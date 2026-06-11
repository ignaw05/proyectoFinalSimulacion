import os
import time
from playwright.sync_api import sync_playwright

def capture(num_images: int, base_filename: str):
    url = "https://share.earthcam.net/tJ90CoLmq7TzrY396Yd88A4kdLdbDd6oQl5D9Ktzt8U/times_square_locations/street_cam/live"
    output_dir = "captures"
    os.makedirs(output_dir, exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            locale="en-US"
        )
        page = context.new_page()
        
        print(f"Navigating to {url}...")
        page.goto(url)
        
        # Use video selector for the EarthCam page
        video_selector = "video"
        
        print("Waiting for the video player to load...")
        page.wait_for_selector(video_selector, timeout=15000)
        
        # Wait a couple of seconds to make sure the video stream starts rendering
        print("Waiting for video stream to start...")
        time.sleep(6)
        
        video_element = page.locator(video_selector)
        video_element.scroll_into_view_if_needed()
        
        print(f"Starting capture of {num_images} screenshots...")
        for i in range(1, num_images + 1):
            filename = f"{base_filename}{i}.png"
            filepath = os.path.join(output_dir, filename)
            
            # Take screenshot of the video element
            video_element.screenshot(path=filepath)
            print(f"Saved: {filepath}")
            
            # Wait 3 milliseconds between captures if it's not the last capture
            if i < num_images:
                time.sleep(3)
                
        browser.close()

if __name__ == "__main__":
    capture(5, "imagen")
