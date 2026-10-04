"""An in-memory fake filesystem for dupfinder.py.

What your code gets is an `fs` object with these methods (and nothing else):

    fs.list_dir(path)   -> list[str]   full paths of the entries in a directory
                                       raises PermissionError if the directory is unreadable
    fs.is_dir(path)     -> bool        True for directories (also for symlinks pointing at one)
    fs.size(path)       -> int         size in bytes, no read needed
    fs.read_file(path)  -> bytes       whole content; raises PermissionError on an unreadable file,
                                       raises MemoryError on a file over LOAD_LIMIT bytes
                                       (pretend those are 40 GB)
    fs.read_chunks(path, chunk_size=1 << 20) -> iterator of bytes   works on files of any size
    fs.identity(path)   -> (dev, inode)  the same file reached through different paths
                                       (via a symlink) has the same identity

Symlinks are followed silently by list_dir / is_dir, so a directory tree can
contain cycles — exactly like a real disk.
"""
import random

LOAD_LIMIT = 4 * 1024 * 1024      # read_file refuses anything larger than this


class _Node:
    __slots__ = ("kind", "children", "content", "big", "target", "denied", "inode")

    def __init__(self, kind, inode):
        self.kind = kind              # "dir" | "file" | "link"
        self.children = {} if kind == "dir" else None
        self.content = b""
        self.big = None               # (seed, size) for generated big files
        self.target = None            # absolute path for links
        self.denied = False
        self.inode = inode


class FakeFS:
    def __init__(self):
        self._next = 1
        self._root = self._new("dir")

    # ---------- building (used by the tests, not by your code) ----------
    def _new(self, kind):
        n = _Node(kind, self._next)
        self._next += 1
        return n

    def _parts(self, path):
        return [p for p in path.split("/") if p]

    def _mkdirs(self, parts):
        cur = self._root
        for p in parts:
            if p not in cur.children:
                cur.children[p] = self._new("dir")
            cur = cur.children[p]
        return cur

    def add_dir(self, path):
        self._mkdirs(self._parts(path))

    def add_file(self, path, content=b"", big=None):
        parts = self._parts(path)
        d = self._mkdirs(parts[:-1])
        f = self._new("file")
        if big is not None:
            f.big = big                 # (seed, size): content is generated on read
        else:
            f.content = content
        d.children[parts[-1]] = f

    def add_symlink(self, path, target):
        parts = self._parts(path)
        d = self._mkdirs(parts[:-1])
        l = self._new("link")
        l.target = target
        d.children[parts[-1]] = l

    def deny(self, path):
        self._resolve(path, follow=False).denied = True

    # ---------- resolution ----------
    def _resolve(self, path, follow=True, _depth=0):
        if _depth > 64:
            raise OSError(f"too many levels of symbolic links: {path}")
        cur = self._root
        parts = self._parts(path)
        for i, p in enumerate(parts):
            if cur.kind == "link":
                cur = self._resolve(cur.target, _depth=_depth + 1)
            if cur.kind != "dir" or p not in cur.children:
                raise FileNotFoundError(path)
            cur = cur.children[p]
        if follow and cur.kind == "link":
            cur = self._resolve(cur.target, _depth=_depth + 1)
        return cur

    def _node_size(self, n):
        return n.big[1] if n.big else len(n.content)

    def _chunks(self, n, chunk_size):
        if n.big is None:
            for i in range(0, len(n.content), chunk_size):
                yield n.content[i:i + chunk_size]
            return
        seed, size = n.big
        done = 0
        i = 0
        while done < size:
            k = min(chunk_size, size - done)
            yield random.Random(seed * 1_000_003 + i).randbytes(k)
            done += k
            i += 1

    # ---------- the interface your code uses ----------
    def list_dir(self, path):
        n = self._resolve(path)
        if n.kind != "dir":
            raise NotADirectoryError(path)
        if n.denied:
            raise PermissionError(path)
        base = path.rstrip("/")
        return [f"{base}/{name}" for name in sorted(n.children)]

    def is_dir(self, path):
        try:
            return self._resolve(path).kind == "dir"
        except (FileNotFoundError, OSError):
            return False

    def size(self, path):
        return self._node_size(self._resolve(path))

    def read_file(self, path):
        n = self._resolve(path)
        if n.kind != "file":
            raise IsADirectoryError(path)
        if n.denied:
            raise PermissionError(path)
        if self._node_size(n) > LOAD_LIMIT:
            raise MemoryError(f"{path}: too large to load at once, use read_chunks")
        return n.content

    def read_chunks(self, path, chunk_size=1 << 20):
        n = self._resolve(path)
        if n.kind != "file":
            raise IsADirectoryError(path)
        if n.denied:
            raise PermissionError(path)
        return self._chunks(n, chunk_size)

    def identity(self, path):
        return (1, self._resolve(path).inode)

    # ---------- ground truth for the tests ----------
    def _truth(self, root="/"):
        """inode -> (content key, one path), for every file a traversal from root may legally read."""
        out = {}
        seen = set()
        stack = [(self._resolve(root), root.rstrip("/"))]
        while stack:
            n, prefix = stack.pop()
            if n.kind == "link":
                n = self._resolve(n.target)
            if n.kind != "dir" or n.denied or n.inode in seen:
                continue
            seen.add(n.inode)
            for name, c in n.children.items():
                if c.kind == "file":
                    if not c.denied:
                        out[c.inode] = (("big",) + c.big if c.big else c.content, prefix + "/" + name)
                else:
                    stack.append((c, prefix + "/" + name))
        return out
