#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Application configuration module."""

import os


class classproperty(property):
    """A descriptor to expose computed class-level properties."""

    def __get__(self, obj, owner):
        return self.fget(owner)


class Config:
    """App configuration with lazy environment lookup."""

    @classproperty
    def GEMINI_API_KEY(cls):
        """Gemini API key loaded lazily at access time."""
        return os.getenv("GEMINI_API_KEY", "")

    @classproperty
    def LINE_CHANNEL_SECRET(cls):
        """LINE channel secret loaded lazily at access time."""
        return os.getenv("LINE_CHANNEL_SECRET", "")

    @classproperty
    def LINE_CHANNEL_ACCESS_TOKEN(cls):
        """LINE channel access token loaded lazily at access time."""
        return os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")

    @classproperty
    def GEMINI_MODEL(cls):
        """Gemini model name with flash as default."""
        return os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    @classproperty
    def SYSTEM_PROMPT(cls):
        """System prompt for translation behavior."""
        return (
            "專業的多國語言翻譯助手，需自動偵測語言並提供道地、"
            "具備文化語境的翻譯"
        )
