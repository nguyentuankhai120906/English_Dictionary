"""
radix_trie.py  –  Radix-Trie (Compressed Trie) Engine
=======================================================
Mỗi node lưu:
  - edge_label : str          – nhãn cạnh dẫn đến node này (chuỗi, KHÔNG phải 1 ký tự)
  - children   : dict[str, RadixTrieNode]   – key = ký tự đầu của edge_label con
  - is_end     : bool         – true nếu đây là cuối một từ hợp lệ
  - is_deleted : bool         – soft-delete (giống C++ isTrash)
  - word       : str | None   – từ gốc (chỉ set khi is_end=True)
  - definition : str | None   – nghĩa (chỉ set khi is_end=True)
"""

from __future__ import annotations
import json
import os
from typing import Optional, Tuple

# ─────────────────────────────────────────────
#  Node
# ─────────────────────────────────────────────
class RadixTrieNode:
    __slots__ = ("edge_label", "children", "is_end", "is_deleted", "word", "definition")

    def __init__(self, edge_label: str = ""):
        self.edge_label:  str  = edge_label
        self.children:    dict = {}          # {first_char -> RadixTrieNode}
        self.is_end:      bool = False
        self.is_deleted:  bool = False
        self.word:        Optional[str] = None
        self.definition:  Optional[str] = None

    # ── Serialize / Deserialize (cho JSON persistence) ────────────────────
    def to_dict(self) -> dict:
        return {
            "edge_label":  self.edge_label,
            "is_end":      self.is_end,
            "is_deleted":  self.is_deleted,
            "word":        self.word,
            "definition":  self.definition,
            "children":    {k: v.to_dict() for k, v in self.children.items()},
        }

    @classmethod
    def from_dict(cls, d: dict) -> "RadixTrieNode":
        node = cls(d["edge_label"])
        node.is_end      = d["is_end"]
        node.is_deleted  = d["is_deleted"]
        node.word        = d["word"]
        node.definition  = d["definition"]
        node.children    = {k: cls.from_dict(v) for k, v in d["children"].items()}
        return node


# ─────────────────────────────────────────────
#  Radix Trie
# ─────────────────────────────────────────────
class RadixTrie:
    """
    Radix Trie (Compressed Trie) cho từ điển tiếng Anh.

    Ký tự hợp lệ: a-z, dấu nháy đơn ('), gạch ngang (-)
    Mọi từ được chuyển thành chữ thường trước khi xử lý.
    """

    VALID_CHARS = set("abcdefghijklmnopqrstuvwxyz'-")
    INDEX_FILE  = "data/index.json"
    STATS_FILE  = "data/stats.json"

    def __init__(self):
        self.root = RadixTrieNode("")   # root: edge_label rỗng
        self._word_count = 0
        os.makedirs("data", exist_ok=True)

    # ══════════════════════════════════════════════
    #  PRIVATE HELPERS
    # ══════════════════════════════════════════════

    @staticmethod
    def _common_prefix_len(a: str, b: str) -> int:
        """Độ dài tiền tố chung của 2 chuỗi."""
        i = 0
        while i < len(a) and i < len(b) and a[i] == b[i]:
            i += 1
        return i

    @staticmethod
    def _validate(word: str) -> str:
        """Chuẩn hóa và kiểm tra từ. Raise ValueError nếu sai."""
        word = word.strip().lower()
        if not word:
            raise ValueError("Từ không được để trống.")
        for ch in word:
            if ch not in RadixTrie.VALID_CHARS:
                raise ValueError(f"Ký tự không hợp lệ: '{ch}'")
        return word

    # ══════════════════════════════════════════════
    #  INSERT  (Add Word)
    # ══════════════════════════════════════════════

    def insert(self, word: str, definition: str) -> Tuple[bool, str]:
        """
        Thêm từ vào trie.
        Trả về (True, message) nếu thành công, (False, message) nếu thất bại.
        """
        try:
            word = self._validate(word)
        except ValueError as e:
            return False, str(e)

        definition = definition.strip()
        if not definition:
            return False, "Nghĩa không được để trống."

        success, msg, _ = self._insert_node(self.root, word, word, definition)
        if success:
            self._word_count += 1
            self.save()
        return success, msg

    def _insert_node(
        self,
        node: RadixTrieNode,
        remaining: str,
        full_word: str,
        definition: str,
    ) -> Tuple[bool, str, RadixTrieNode]:
        """Đệ quy insert. Trả về (ok, msg, node_cập_nhật_cuối)."""

        if not remaining:
            # Đã đến đúng node
            if node.is_end and not node.is_deleted:
                return False, f"Từ '{full_word}' đã tồn tại.", node
            node.is_end      = True
            node.is_deleted  = False
            node.word        = full_word
            node.definition  = definition
            return True, f"✓ Đã thêm '{full_word}'.", node

        first_ch = remaining[0]

        if first_ch not in node.children:
            # Không có cạnh nào bắt đầu bằng first_ch → tạo node mới
            new_node = RadixTrieNode(remaining)
            new_node.is_end     = True
            new_node.word       = full_word
            new_node.definition = definition
            node.children[first_ch] = new_node
            return True, f"✓ Đã thêm '{full_word}'.", new_node

        child = node.children[first_ch]
        cp = self._common_prefix_len(remaining, child.edge_label)

        if cp == len(child.edge_label):
            # remaining bắt đầu đúng bằng edge_label của child → đi sâu hơn
            return self._insert_node(child, remaining[cp:], full_word, definition)

        # Cần SPLIT node child tại vị trí cp
        # ┌ Trước split: [node] ──(edge_label)──> [child]
        # └ Sau  split:  [node] ──(edge_label[:cp])──> [mid] ──(edge_label[cp:])──> [child]
        #                                                  └──(remaining[cp:])──> [new_leaf]
        mid = RadixTrieNode(child.edge_label[:cp])   # node trung gian

        # Child cũ đổi edge_label thành phần còn lại
        child.edge_label = child.edge_label[cp:]
        mid.children[child.edge_label[0]] = child

        # Node mới cho từ đang insert
        new_leaf = RadixTrieNode(remaining[cp:])
        new_leaf.is_end     = True
        new_leaf.word       = full_word
        new_leaf.definition = definition

        if remaining[cp:]:
            mid.children[remaining[cp]] = new_leaf
        else:
            # remaining kết thúc đúng tại mid
            mid.is_end      = True
            mid.word        = full_word
            mid.definition  = definition

        node.children[first_ch] = mid
        return True, f"✓ Đã thêm '{full_word}' (trie đã split).", mid

    # ══════════════════════════════════════════════
    #  SEARCH  (Tìm nghĩa)
    # ══════════════════════════════════════════════

    def search(self, word: str) -> Tuple[bool, str]:
        """
        Tìm nghĩa của từ.
        Trả về (True, definition) hoặc (False, thông báo lỗi).
        """
        try:
            word = self._validate(word)
        except ValueError as e:
            return False, str(e)

        node = self._search_node(self.root, word)
        if node is None:
            return False, f"✗ Không tìm thấy '{word}'."
        if node.is_deleted:
            return False, f"✗ Từ '{word}' đã bị xóa."
        return True, node.definition

    def _search_node(self, node: RadixTrieNode, remaining: str) -> Optional[RadixTrieNode]:
        if not remaining:
            return node if node.is_end else None

        first_ch = remaining[0]
        if first_ch not in node.children:
            return None

        child = node.children[first_ch]
        cp = self._common_prefix_len(remaining, child.edge_label)

        if cp < len(child.edge_label):
            return None   # remaining không khớp hoàn toàn với edge_label

        return self._search_node(child, remaining[cp:])

    # ══════════════════════════════════════════════
    #  DELETE  (Xóa từ – soft delete)
    # ══════════════════════════════════════════════

    def delete(self, word: str) -> Tuple[bool, str]:
        """
        Xóa mềm (soft delete) giống C++ MarkAsDelete.
        Trả về (True, message) hoặc (False, message).
        """
        try:
            word = self._validate(word)
        except ValueError as e:
            return False, str(e)

        node = self._search_node(self.root, word)
        if node is None or not node.is_end:
            return False, f"✗ Từ '{word}' không tồn tại."
        if node.is_deleted:
            return False, f"✗ Từ '{word}' đã bị xóa trước đó."

        node.is_deleted = True
        self._word_count = max(0, self._word_count - 1)
        self.save()
        return True, f"✓ Đã xóa '{word}'."

    # ══════════════════════════════════════════════
    #  PURGE  (Xóa cứng – tương đương CleanTrash)
    # ══════════════════════════════════════════════

    def purge_deleted(self) -> int:
        """Xóa vĩnh viễn tất cả node bị đánh dấu deleted. Trả về số node đã xóa."""
        count = [0]
        self._purge_recursive(self.root, count)
        self.save()
        return count[0]

    def _purge_recursive(self, node: RadixTrieNode, count: list):
        to_remove = []
        for key, child in node.children.items():
            if child.is_deleted and not child.children:
                to_remove.append(key)
                count[0] += 1
            else:
                self._purge_recursive(child, count)

        for key in to_remove:
            del node.children[key]

    # ══════════════════════════════════════════════
    #  LIST ALL WORDS
    # ══════════════════════════════════════════════

    def get_all_words(self, include_deleted: bool = False) -> list[dict]:
        """Trả về list tất cả các từ (theo thứ tự alphabet)."""
        result = []
        self._collect(self.root, result, include_deleted)
        result.sort(key=lambda x: x["word"])
        return result

    def _collect(self, node: RadixTrieNode, result: list, include_deleted: bool):
        if node.is_end:
            if include_deleted or not node.is_deleted:
                result.append({
                    "word":       node.word,
                    "definition": node.definition,
                    "deleted":    node.is_deleted,
                })
        for child in node.children.values():
            self._collect(child, result, include_deleted)

    # ══════════════════════════════════════════════
    #  VISUALIZE TRIE STRUCTURE
    # ══════════════════════════════════════════════

    def visualize(self, max_depth: int = 99) -> str:
        """Trả về chuỗi hiển thị cấu trúc trie dạng cây."""
        lines = ["[ROOT]"]
        self._viz_recursive(self.root, "", True, lines, 0, max_depth)
        return "\n".join(lines)

    def _viz_recursive(
        self,
        node: RadixTrieNode,
        prefix: str,
        is_last: bool,
        lines: list,
        depth: int,
        max_depth: int,
    ):
        if depth > max_depth:
            return
        children = list(node.children.values())
        for i, child in enumerate(children):
            is_child_last = (i == len(children) - 1)
            connector = "└── " if is_child_last else "├── "
            branch    = "    " if is_child_last else "│   "

            label = f'"{child.edge_label}"'
            if child.is_end:
                status = " [DELETED]" if child.is_deleted else f" ★ {child.word}"
                label += status
            lines.append(prefix + connector + label)
            self._viz_recursive(child, prefix + branch, is_child_last, lines, depth + 1, max_depth)

    # ══════════════════════════════════════════════
    #  PERSISTENCE
    # ══════════════════════════════════════════════

    def save(self):
        os.makedirs("data", exist_ok=True)
        with open(self.INDEX_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "word_count": self._word_count,
                "trie":       self.root.to_dict(),
            }, f, ensure_ascii=False, indent=2)

    def load(self) -> bool:
        if not os.path.exists(self.INDEX_FILE):
            return False
        try:
            with open(self.INDEX_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.root         = RadixTrieNode.from_dict(data["trie"])
            self._word_count  = data.get("word_count", 0)
            return True
        except Exception:
            return False

    @property
    def word_count(self) -> int:
        return self._word_count
