import click
import requests
import os
from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper

from .commons import require_login, API_BASE, unwrap_response


@click.command(name="image-upload")
@click.argument("image", nargs=1, required=True)
@click.argument("file", nargs=1, required=True)
@require_login
def cmd_image_upload(ctx, image, file):
    """Upload an image to the server."""
    # resolve file path
    # upload file
    if os.path.isabs(file):
        file_path = file
    else:
        file_path = os.path.join(os.getcwd(), file)

    if not os.path.exists(file_path):
        print("[-] File not found: %s" % file_path)
        exit()

    resp = requests.get(
        API_BASE + "/manage/images/upload",
        headers=ctx.obj['API_HEADERS'],
        params={
            "name": os.path.basename(file_path),
            "parts": 1,
        },
    )

    data = unwrap_response(resp)
    upload_id = data['uploadId']
    upload_url, = tuple(data['urls'])
    print("[+] Upload ID: %s" % upload_id)
    file_size = os.stat(file_path).st_size

    with open(file_path, "rb") as f:
        with tqdm(total=file_size, unit="B", unit_scale=True, unit_divisor=1024) as t:
            wrapped_file = CallbackIOWrapper(t.update, f, "read")
            resp = requests.put(upload_url, data=wrapped_file)
            etag = resp.headers['ETag']
    part = {
        "part": 1,
        "etag": etag,
    }
    resp = requests.post(
        API_BASE + "/manage/images/complete-upload",
        headers=ctx.obj['API_HEADERS'],
        params={
            "id": image,
        },
        json={
            "key": data['key'],
            "uploadId": upload_id,
            "parts": [part],
        },
    )
    unwrap_response(resp)
    print("[+] Done!")
