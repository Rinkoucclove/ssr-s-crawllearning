"""
页面解析器模块
负责解析新闻站点页面
"""
import logging
import re
import json
from typing import List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from ..models import Article
from ..config import (
    MAX_PAGES,
    MEDIA_EXTENSIONS,
    ATTACHMENT_EXTENSIONS,
    CONTENT_SELECTORS,
    TITLE_SELECTORS,
    FILTER_KEYWORDS
)


class NewsPageParser:
    """
    新闻页面解析器（针对 https://ptext.nju.edu.cn）

    思路：
    - 从首页开始，站内 BFS，收集所有 /info/xxx.htm 详情页 URL
    - 针对每个详情页解析标题 / 日期 / 正文 / 图片 / 点击量
    """

    def __init__(self, session_manager, base_domain: str):
        """
        初始化解析器

        Args:
            session_manager: 会话管理器实例
            base_domain: 站点域名
        """
        self.session_manager = session_manager
        self.base_domain = base_domain.rstrip('/')
        self._compile_patterns()

    def _compile_patterns(self):
        """预编译正则表达式模式"""
        # 确保配置是列表类型
        media_exts = MEDIA_EXTENSIONS if isinstance(MEDIA_EXTENSIONS, list) else []
        attach_exts = ATTACHMENT_EXTENSIONS if isinstance(ATTACHMENT_EXTENSIONS, list) else []

        self.file_ext_pattern = re.compile(
            r'\.(' + '|'.join(media_exts) + r')(?:\?|$)',
            re.IGNORECASE
        )
        self.attach_pattern = re.compile(
            r'\.(' + '|'.join(attach_exts) + r')(?:\?|$)',
            re.IGNORECASE
        )

    def collect_info_page_urls(self, start_url: str, max_pages: int = None) -> List[str]:
        """
        从 start_url 出发，站内 BFS，收集所有 /info/xxx.htm 详情页

        Args:
            start_url: 起始URL
            max_pages: 最多遍历的页面数，默认使用配置值

        Returns:
            List[str]: 详情页URL列表
        """
        if max_pages is None:
            max_pages = MAX_PAGES

        logging.info(f"开始站内遍历，起始URL: {start_url}")

        visited = set()
        queue = [start_url]
        info_urls = set()

        while queue and len(visited) < max_pages:
            current_url = queue.pop(0)
            if current_url in visited:
                continue

            visited.add(current_url)
            logging.info(f"遍历页面 {len(visited)}/{max_pages}: {current_url}")

            soup = self.session_manager.get_page(current_url)
            if not soup:
                continue

            # 收集当前页面上的所有链接
            for a in soup.find_all('a', href=True):
                href = a['href'].strip()
                if not href or href.startswith(('javascript:', '#', 'mailto:')):
                    continue

                full_url = urljoin(current_url, href)
                # 限制在本站内
                if not full_url.startswith(self.base_domain):
                    continue

                # 跳过明显是附件 / 多媒体文件的链接
                if self.file_ext_pattern.search(full_url):
                    continue

                # 收集 info 详情页
                if '/info/' in full_url and full_url.endswith('.htm'):
                    info_urls.add(full_url)

                # 加入待遍历队列
                if full_url not in visited and full_url not in queue:
                    queue.append(full_url)

        logging.info(f"站点遍历结束，共遍历 {len(visited)} 个页面，发现 {len(info_urls)} 个 info 详情页")
        return sorted(info_urls)

    def parse_news_detail(self, news_url: str) -> Optional[Article]:
        """
        解析新闻详情页

        Args:
            news_url: 新闻详情页URL

        Returns:
            Article: 解析后的文章对象，失败返回None
        """
        soup = self.session_manager.get_page(news_url)
        if not soup:
            return None

        article = Article(url=news_url)

        try:
            # ===== 1. 标题 =====
            article.title = self._extract_title(soup, news_url)

            # ===== 2. 时间（日期）=====
            article.publish_time = self._extract_publish_time(soup)

            # ===== 3. 点击量 =====
            article.clicks = self._extract_clicks(soup, news_url)

            # ===== 4. 正文内容 =====
            article.content = self._extract_content(soup)

            # ===== 5. 图片链接 =====
            article.img_url = self._extract_images(soup, news_url)

            # ===== 6. 附件链接（doc/pdf/zip 等）=====
            article.attchment = self._extract_attachments(soup, news_url)
            article.truncate_attachment()

            # ===== 7. 生成哈希ID =====
            article.generate_hash_id()

            # 验证文章有效性
            if article.is_valid():
                logging.info(f"成功解析: {article.title}, Hash ID: {article.hash_id}")
                return article
            else:
                logging.warning(f"文章数据不完整（缺少标题或URL）: {news_url}")
                return None

        except Exception as e:
            logging.error(f"解析新闻详情页时发生错误 ({news_url}): {e}")
            return None

    def _extract_title(self, soup: BeautifulSoup, fallback_url: str) -> str:
        """提取文章标题"""
        title_elem = None
        for selector in TITLE_SELECTORS:
            title_elem = soup.select_one(selector)
            if title_elem:
                break

        if title_elem:
            return title_elem.get_text(strip=True)
        elif soup.title:
            return soup.title.get_text(strip=True)
        else:
            return ""

    def _extract_publish_time(self, soup: BeautifulSoup) -> str:
        """提取发布时间"""
        full_text = soup.get_text(" ", strip=True)

        # 优先匹配"日期：2024-05-06 / 发布时间：2024-05-06"
        m = re.search(r'(?:日期|发布时间)[：:]\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})', full_text)
        if m:
            return m.group(1).replace('/', '-')
        else:
            # 退化：抓文中出现的第一个日期
            m2 = re.search(r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})', full_text)
            if m2:
                return m2.group(1).replace('/', '-')

        return ""

    def _extract_clicks(self, soup: BeautifulSoup, news_url: str) -> str:
        """提取点击量"""
        clicks = ""

        # 尝试从脚本中的 _showDynClicks 获取
        for script in soup.find_all('script'):
            if not script.string:
                continue
            sm = re.search(
                r'_showDynClicks\("(\w+)",\s*(\d+),\s*(\d+)\)',
                script.string
            )
            if sm:
                clicktype, owner, clickid = sm.groups()
                api_url = urljoin(self.base_domain,
                                  '/system/resource/code/news/click/dynclicks.jsp')
                try:
                    extra_headers = {
                        "Referer": news_url,
                        "X-Requested-With": "XMLHttpRequest",
                    }
                    resp = self.session_manager.get_raw(
                        api_url,
                        params={
                            "clicktype": clicktype,
                            "owner": owner,
                            "clickid": clickid,
                        },
                        extra_headers=extra_headers,
                        timeout=10
                    )
                    if resp and resp.status_code == 200:
                        txt = resp.text.strip()
                        try:
                            data = json.loads(txt)
                            clicks_val = data.get("wbshowtimes", 0)
                        except Exception:
                            nm = re.search(r'(\d+)', txt)
                            clicks_val = int(nm.group(1)) if nm else 0
                        clicks = str(clicks_val)
                        logging.info(f"动态获取点击量成功: {clicks}")
                except Exception as e:
                    logging.error(f"调用点击量API失败: {e}")
                break

        # 如果脚本没拿到，就在文本里搜"浏览次数 / 点击次数"
        if not clicks:
            for t in soup.stripped_strings:
                if '浏览次数' in t or '点击次数' in t or '点击量' in t:
                    nm = re.search(r'(\d+)', t)
                    if nm:
                        clicks = nm.group(1)
                        break

        return clicks

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """提取正文内容"""
        content_div = None
        for selector in CONTENT_SELECTORS:
            content_div = soup.select_one(selector)
            if content_div:
                break

        if content_div:
            paragraphs = self._extract_content_paragraphs(content_div)
            # 确保 paragraphs 是列表类型
            if isinstance(paragraphs, list):
                return '\n\n'.join(paragraphs)
            elif isinstance(paragraphs, str):
                return paragraphs
            else:
                return ""
        return ""

    def _extract_content_paragraphs(self, content_div) -> List[str]:
        """
        提取内容段落：
        - 第一轮：严格用 <p>，过滤时间/导航，长度>=8
        - 如果一段都抓不到，再兜底在 <div>/<span>/<li> 等里找文本
        """
        paragraphs = []
        seen_texts = set()

        # 第一轮：相对干净，只看 <p>
        for p in content_div.find_all('p'):
            text = p.get_text(strip=True)
            if not text:
                continue

            # 排除时间/日期等元信息
            if p.find_parents(class_=['conttime', 'time', 'date']):
                continue

            # 过滤明显不是正文的尾部信息
            if any(bad in text for bad in FILTER_KEYWORDS):
                continue

            if len(text) >= 8 and text not in seen_texts:
                seen_texts.add(text)
                paragraphs.append(text)

        if paragraphs:
            return paragraphs

        # 第二轮兜底：p 里啥也没抓到，再看 <div> / <span> / <li> 里的文字
        for tag in content_div.find_all(['div', 'p', 'span', 'li']):
            text = tag.get_text(strip=True)
            if not text:
                continue

            if any(bad in text for bad in FILTER_KEYWORDS):
                continue

            if len(text) >= 4 and text not in seen_texts:
                seen_texts.add(text)
                paragraphs.append(text)

        return paragraphs

    def _extract_images(self, soup: BeautifulSoup, news_url: str) -> List[str]:
        """提取图片链接"""
        img_urls = []
        imgs = soup.find_all('img')
        for img in imgs:
            src = img.get('src')
            if src:
                if src.startswith(('http://', 'https://')):
                    full_img_url = src
                elif src.startswith('//'):
                    full_img_url = 'https:' + src
                else:
                    full_img_url = urljoin(news_url, src)
                img_urls.append(full_img_url)
        return img_urls

    def _extract_attachments(self, soup: BeautifulSoup, news_url: str) -> str:
        """提取附件链接"""
        attachments = []
        for a in soup.find_all('a', href=True):
            href = a['href'].strip()
            if not href:
                continue
            if self.attach_pattern.search(href):
                full_attach_url = urljoin(news_url, href)
                attachments.append(full_attach_url)

        if attachments:
            return attachments[0]
        return ""
