"""
SSL适配器模块
提供自定义SSL上下文配置，用于处理HTTPS请求
"""
import ssl
from requests.adapters import HTTPAdapter
from typing import Optional


class SSLAdapter(HTTPAdapter):
    """
    自定义SSL适配器，支持灵活的SSL配置
    """

    def __init__(self, ssl_context: Optional[ssl.SSLContext] = None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        """
        初始化连接池时注入SSL上下文
        """
        if self.ssl_context is not None:
            kwargs['ssl_context'] = self.ssl_context
        return super().init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        """
        初始化代理管理器时注入SSL上下文
        """
        if self.ssl_context is not None:
            kwargs['ssl_context'] = self.ssl_context
        return super().proxy_manager_for(*args, **kwargs)


def create_default_ssl_context() -> ssl.SSLContext:
    """
    创建默认的SSL上下文，使用TLS 1.2协议

    Returns:
        ssl.SSLContext: 配置好的SSL上下文
    """
    ctx = ssl.create_default_context()
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.maximum_version = ssl.TLSVersion.TLSv1_2

    try:
        # 降低安全级别以兼容旧服务器
        ctx.set_ciphers('DEFAULT:@SECLEVEL=1')
    except ssl.SSLError:
        # 如果设置失败，使用默认配置
        pass

    return ctx
