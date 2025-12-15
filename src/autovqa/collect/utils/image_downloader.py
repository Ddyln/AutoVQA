from pathlib import Path
from urllib.parse import urlparse

import aiohttp
from tqdm.asyncio import tqdm_asyncio

# from autovqa.collect.utils.data_configs import *


def safe_name_from_url(url: str) -> str:
    """
    Lấy tên file an toàn từ URL (tránh chứa query string).

    Args:
        url (str): Đường dẫn URL ảnh.

    Returns:
        str: Tên file an toàn (ví dụ: "image.jpg").

    Example:
        >>> safe_name_from_url("https://example.com/path/to/photo.jpg?size=200")
        'photo.jpg'
        >>> safe_name_from_url(""https://example.com/")
        'image'
    """
    # Lấy phần tên file từ URL path
    name = Path(urlparse(url).path).name or "image"
    # Nếu tên file chứa query (vd: image.jpg?size=200) -> bỏ phần sau '?'
    return name.split("?")[0] or "image"


async def fetch_image(session: aiohttp.ClientSession, url: str, out_dir: Path) -> Path:
    """
    Tải 1 ảnh từ URL và lưu vào thư mục out_dir.

    Args:
        session (aiohttp.ClientSession): Phiên HTTP dùng chung cho nhiều request.
        url (str): Đường dẫn URL ảnh.
        out_dir (Path): Thư mục lưu ảnh.

    Returns:
        Path: Đường dẫn file đã lưu.
    """
    # Gửi request GET
    async with session.get(url) as resp:
        # Nếu HTTP status != 200 -> báo lỗi
        if resp.status != 200:
            raise RuntimeError(f"Lỗi {resp.status} với URL: {url}")

        # Lấy kiểu dữ liệu của nội dung (vd: image/jpeg)
        ctype = resp.headers.get("Content-Type", "")
        if not ctype.startswith("image/"):
            raise ValueError(f"Không phải ảnh: {url} ({ctype})")

        # Lấy tên file an toàn
        name = safe_name_from_url(url)
        # Nếu tên file chưa có phần mở rộng, thêm từ Content-Type
        if "." not in Path(name).suffix:
            ext = ctype.split("/", 1)[-1]  # vd: "jpeg" từ "image/jpeg"
            name = f"{name}.{ext}"

        out_path = out_dir / name

        # Ghi file theo từng chunk 8KB để tiết kiệm RAM
        with open(out_path, "wb") as f:
            while True:
                chunk = await resp.content.read(8192)
                if not chunk:
                    break
                f.write(chunk)

        return out_path


async def download_many(urls: list[str], out_dir="downloads_async") -> list[Path]:
    """
    Tải nhiều ảnh song song từ danh sách URL.

    Args:
        urls (list[str]): Danh sách URL ảnh.
        out_dir (str, optional): Thư mục lưu ảnh. Mặc định "downloads_async".

    Returns:
        list[Path]: Danh sách đường dẫn file đã lưu.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    timeout = aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(
        timeout=timeout, headers={"User-Agent": "aiohttp"}
    ) as session:
        tasks = [fetch_image(session, u, out_dir) for u in urls]
        # tqdm_asyncio cho thanh tiến trình đẹp
        return await tqdm_asyncio.gather(
            *tasks, total=len(tasks), desc="Downloading images", unit="file"
        )


# Trong notebook thì chạy: await download_many(urls)
