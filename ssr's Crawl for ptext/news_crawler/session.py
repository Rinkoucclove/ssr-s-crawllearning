"""
会话管理器模块
管理HTTP会话和请求
"""
import logging
from typing import Optional, Dict
import requests
from bs4 import BeautifulSoup
from .utils.ssl_adapter import SSLAdapter, create_default_ssl_context
from .config import TIMEOUT


class NewsSessionManager:
    """
    新闻会话管理器
    负责创建安全的HTTP会话并执行页面请求
    """

    def __init__(self, headers: Dict[str, str]):
        """
        初始化会话管理器

        Args:
            headers: HTTP请求头
        """
        self.headers = headers
        self.session = self._create_secure_session()

    def _create_secure_session(self) -> requests.Session:
        """
        创建带SSL配置的安全会话

        Returns:
            requests.Session: 配置好的会话对象
        """
        ssl_context = create_default_ssl_context()
        session = requests.Session()
        session.mount('https://', SSLAdapter(ssl_context))
        return session

    def get_page(self, url: str, timeout: int = None) -> Optional[BeautifulSoup]:
        """
        获取页面并返回BeautifulSoup对象

        Args:
            url: 目标URL
            timeout: 超时时间（秒），默认使用配置值

        Returns:
            BeautifulSoup: 解析后的页面对象，失败返回None
        """
        if timeout is None:
            timeout = TIMEOUT

        try:
            response = self.session.get(url, headers=self.headers, timeout=timeout)
            response.encoding = response.apparent_encoding
            response.raise_for_status()
            # 使用 html.parser（Python 标准库，无需额外安装）
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            logging.error(f"获取页面 {url} 失败: {e}")
            return None

    def get_raw(self, url: str, params: dict = None, timeout: int = None, extra_headers: dict = None) -> Optional[requests.Response]:
        """
        获取原始响应对象（用于API调用）

        Args:
            url: 目标URL
            params: 请求参数
            timeout: 超时时间
            extra_headers: 额外的请求头

        Returns:
            requests.Response: 响应对象，失败返回None
        """
        if timeout is None:
            timeout = TIMEOUT

        headers = self.headers.copy()
        if extra_headers:
            headers.update(extra_headers)

        try:
            response = self.session.get(url, params=params, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response
        except Exception as e:
            logging.error(f"API请求 {url} 失败: {e}")
            return None

    def close(self):
        """
        关闭会话
        """
        if self.session:
            self.session.close()
