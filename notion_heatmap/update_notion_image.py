import requests

NOTION_TOKEN = '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'
NOTION_PAGE_ID = '20ba6b2eb1ea8055a7e4c6c541d1e972'  # Page where you want to embed the heatmap image
IMAGE_URL = 'https://raw.githubusercontent.com/yourusername/notion-heatmap-images/gh-pages/images/heatmap.png'

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def get_page_blocks(page_id):
    url = f"https://api.notion.com/v1/blocks/{page_id}/children?page_size=100"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def delete_block(block_id):
    url = f"https://api.notion.com/v1/blocks/{block_id}"
    response = requests.delete(url, headers=headers)
    return response.status_code

def append_image_block(page_id, image_url):
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    data = {
        "children": [
            {
                "object": "block",
                "type": "image",
                "image": {
                    "type": "external",
                    "external": {
                        "url": image_url
                    }
                }
            }
        ]
    }
    response = requests.patch(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def main():
    # Get existing blocks on the page
    blocks = get_page_blocks(NOTION_PAGE_ID)
    image_blocks = [b for b in blocks['results'] if b['type'] == 'image']

    # Optional: Delete previous image blocks to keep only latest
    for block in image_blocks:
        delete_block(block['id'])

    # Append new image block with updated heatmap
    append_image_block(NOTION_PAGE_ID, IMAGE_URL)
    print("Notion page updated with new heatmap image.")

if __name__ == "__main__":
    main()
