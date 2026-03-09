"""
数据模型模块
定义新闻文章的数据结构
"""
import hashlib
from dataclasses import dataclass, asdict
from typing import List
from .config import ATTACHMENT_MAX_LENGTH


@dataclass
class Article:
    """文章数据类，对应 MySQL 表 bksy_news"""

    # —— 对应表字段 —— #
    url: str = ""
    title: str = ""
    publish_time: str = ""   # 统一为 'YYYY-MM-DD' 字符串，方便直接插入 DATE
    content: str = ""
    attchment: str = ""      # 注意拼写，跟表结构一致

    # —— 额外字段（用于去重和扩展） —— #
    img_url: List[str] = None
    clicks: str = ""
    hash_id: str = ""

    def __post_init__(self):
        """初始化后处理，确保 img_url 是列表类型"""
        if self.img_url is None or not isinstance(self.img_url, list):
            self.img_url = []

    def to_dict(self) -> dict:
        """
        将文章对象转换为字典
        """
        return asdict(self)

    def is_valid(self) -> bool:
        """
        只要求"标题 + URL"非空即可视为一篇有效文章。
        允许纯图片、纯短文本等情况。
        """
        return bool(self.title.strip() and self.url.strip())

    def generate_hash_id(self) -> str:
        """
        生成基于 标题 + URL + 时间 + 正文 + 图片链接 + 附件 的 MD5 哈希值作为唯一标识。
        即使没有正文内容，只要有标题/URL/附件/图片也能生成 hash。
        """
        # 确保 img_url 是列表类型
        img_urls = self.img_url if isinstance(self.img_url, list) else []
        img_part = ','.join(sorted(img_urls))
        data_to_hash = f"{self.title}|{self.url}|{self.publish_time}|{self.content}|{img_part}|{self.attchment}"
        self.hash_id = hashlib.md5(data_to_hash.encode('utf-8')).hexdigest()
        return self.hash_id

    def truncate_attachment(self) -> None:
        """
        截断附件URL以适配数据库字段长度限制
        """
        if self.attchment and len(self.attchment) > ATTACHMENT_MAX_LENGTH:
            self.attchment = self.attchment[:ATTACHMENT_MAX_LENGTH]
