"""Read the official archived MaStR ZIP through strict HTTP byte ranges.

Isolated research branch; no production site modifications or credentials.
ZIP central directory and individual members are read without downloading solar data.
"""
import io
import time
import urllib.request

MAX_TRANSFER = 12 * 1024 * 1024

class HttpRangeFile(io.RawIOBase):
    def __init__(self, url):
        self.url = url
        req = urllib.request.Request(url, method="HEAD", headers={"Accept-Encoding": "identity", "User-Agent": "Research-MaStR-2026/1.0"})
        last_error = None
        for attempt in range(8):
            try:
                with urllib.request.urlopen(req, timeout=75) as response:
                    self.length = int(response.headers["Content-Length"])
                    self.etag = response.headers.get("ETag")
                    self.accept_ranges = response.headers.get("Accept-Ranges", "")
                break
            except (OSError, ValueError) as exc:
                last_error = exc
                if attempt < 7:
                    time.sleep(min(2 * (attempt + 1), 15))
        else:
            raise RuntimeError(f"Eight attempts could not open official ZIP header: {last_error}")
        if self.accept_ranges.lower() != "bytes":
            raise ValueError("Source does not support HTTP byte ranges")
        self.pos = 0
        self.range_start = 0
        self.cache = b""
        self.bytes_transferred = 0
        self.range_requests = 0

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, offset, whence=io.SEEK_SET):
        if whence == io.SEEK_CUR:
            offset += self.pos
        elif whence == io.SEEK_END:
            offset += self.length
        elif whence != io.SEEK_SET:
            raise ValueError(whence)
        if offset < 0 or offset > self.length:
            raise ValueError("Invalid archive offset")
        self.pos = offset
        return self.pos

    def _range(self, start, requested):
        end = min(self.length, start + min(MAX_TRANSFER, max(512 * 1024, requested))) - 1
        target = f"bytes {start}-{end}/{self.length}"
        req = urllib.request.Request(
            self.url,
            headers={"Range": f"bytes={start}-{end}",
                     "Accept-Encoding": "identity",
                     "User-Agent": "Research-MaStR-2026/1.0"},
        )
        error = None
        for retry in range(6):
            try:
                with urllib.request.urlopen(req, timeout=110) as response:
                    data = response.read()
                    if response.status != 206:
                        raise ValueError(f"Ranged request status {response.status}")
                    if response.headers.get("Content-Range") != target:
                        raise ValueError("Source content range mismatch")
                    if self.etag and response.headers.get("ETag") not in (None, self.etag):
                        raise ValueError("Source archive ETag changed")
                    if len(data) != end - start + 1:
                        raise ValueError("Truncated HTTP range")
                self.range_start = start
                self.cache = data
                self.range_requests += 1
                self.bytes_transferred += len(data)
                return
            except (OSError, ValueError) as exc:
                error = exc
                if retry < 5:
                    time.sleep(2 * (retry + 1))
        raise RuntimeError(f"Unable to read official source range: {error}")

    def read(self, size=-1):
        if size is None or size < 0:
            size = self.length - self.pos
        size = min(size, self.length - self.pos)
        if size <= 0:
            return b""
        parts = []
        while size:
            if not (self.range_start <= self.pos < self.range_start + len(self.cache)):
                self._range(self.pos, size)
            k = min(size, self.range_start + len(self.cache) - self.pos)
            offset = self.pos - self.range_start
            parts.append(self.cache[offset:offset + k])
            self.pos += k
            size -= k
        return b"".join(parts)
