#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置管理模組

此模組負責管理應用程式的所有配置，包括環境變數的讀取和驗證。
遵循應用程式工廠模式，使用 python-dotenv 管理敏感信息。
"""

import os
from typing import Optional


class Config:
    """
    應用程式基礎配置類。
    
    此類提供動態讀取環境變數的方法，確保敏感信息
    不會被硬編碼在源代碼中，並支持運行時環境變更。
    
    所有配置值都動態讀取，確保在 load_dotenv() 之後獲得正確值。
    """
    
    # Flask 配置
    @classmethod
    def get_secret_key(cls) -> str:
        """獲取 Flask Secret Key。"""
        return os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    @classmethod
    def get_debug(cls) -> bool:
        """獲取調試模式設定。"""
        return os.getenv("FLASK_DEBUG", "False").lower() == "true"
    
    # LINE Messaging API 配置
    @classmethod
    def get_line_channel_access_token(cls) -> str:
        """獲取 LINE Channel Access Token。"""
        return os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
    
    @classmethod
    def get_line_channel_secret(cls) -> str:
        """獲取 LINE Channel Secret。"""
        return os.getenv("LINE_CHANNEL_SECRET", "")
    
    # Google Gemini API 配置
    @classmethod
    def get_gemini_api_key(cls) -> str:
        """獲取 Gemini API Key。"""
        return os.getenv("GEMINI_API_KEY", "")
    
    @classmethod
    def get_gemini_model(cls) -> str:
        """獲取 Gemini 模型名稱（預設為 gemini-1.5-flash）。"""
        return os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    @classmethod
    def get_gemini_fallback_models(cls) -> list:
        """獲取 Gemini 備援模型列表（逗號分隔）。"""
        raw = os.getenv("GEMINI_FALLBACK_MODELS", "")
        if not raw.strip():
            return []
        return [model.strip() for model in raw.split(",") if model.strip()]
    
    # 應用程式設置
    @classmethod
    def get_port(cls) -> int:
        """獲取應用程式監聽端口。"""
        return int(os.getenv("PORT", "5000"))
    
    @classmethod
    def get_log_level(cls) -> str:
        """獲取日誌級別。"""
        return os.getenv("LOG_LEVEL", "INFO")
    
    # 翻譯設置
    @classmethod
    def get_default_target_language(cls) -> str:
        """獲取預設目標語言。"""
        return os.getenv("DEFAULT_TARGET_LANGUAGE", "zh-TW")
    
    @classmethod
    def get_max_message_length(cls) -> int:
        """獲取訊息最大長度。"""
        return int(os.getenv("MAX_MESSAGE_LENGTH", "1000"))
    
    # 為保持向後兼容性，保留屬性訪問方式
    @property
    def SECRET_KEY(self) -> str:
        return self.get_secret_key()
    
    @property
    def DEBUG(self) -> bool:
        return self.get_debug()
    
    @property
    def TESTING(self) -> bool:
        return False
    
    @property
    def LINE_CHANNEL_ACCESS_TOKEN(self) -> str:
        return self.get_line_channel_access_token()
    
    @property
    def LINE_CHANNEL_SECRET(self) -> str:
        return self.get_line_channel_secret()
    
    @property
    def GEMINI_API_KEY(self) -> str:
        return self.get_gemini_api_key()
    
    @property
    def GEMINI_MODEL(self) -> str:
        return self.get_gemini_model()
    
    @property
    def PORT(self) -> int:
        return self.get_port()
    
    @property
    def LOG_LEVEL(self) -> str:
        return self.get_log_level()
    
    @property
    def DEFAULT_TARGET_LANGUAGE(self) -> str:
        return self.get_default_target_language()
    
    @property
    def MAX_MESSAGE_LENGTH(self) -> int:
        return self.get_max_message_length()
    
    @classmethod
    def validate(cls) -> bool:
        """
        驗證必要的配置是否已設置。
        
        Returns:
            bool: 所有必要配置都已設置時返回 True，否則返回 False
            
        Raises:
            ValueError: 當缺少必要的配置時拋出異常
        """
        required_checks = {
            "LINE_CHANNEL_ACCESS_TOKEN": cls.get_line_channel_access_token(),
            "LINE_CHANNEL_SECRET": cls.get_line_channel_secret(),
            "GEMINI_API_KEY": cls.get_gemini_api_key()
        }
        
        missing = [key for key, value in required_checks.items() if not value]
        
        if missing:
            raise ValueError(
                f"缺少必要的環境變數配置: {', '.join(missing)}"
            )
        
        return True


class DevelopmentConfig(Config):
    """開發環境配置（向後兼容）"""
    pass


class TestingConfig(Config):
    """測試環境配置（向後兼容）"""
    pass


class ProductionConfig(Config):
    """生產環境配置（向後兼容）"""
    pass


def get_config(env: Optional[str] = None) -> type:
    """
    根據環境取得相應的配置類。
    
    Args:
        env: 環境名稱 ('development', 'testing', 'production')
             若不指定，從 FLASK_ENV 環境變數取得
    
    Returns:
        type: 相應的配置類
        
    Example:
        >>> config = get_config("development")
        >>> config.get_gemini_model()
    """
    if env is None:
        env = os.getenv("FLASK_ENV", "development")
    
    config_map = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig
    }
    
    return config_map.get(env, DevelopmentConfig)
