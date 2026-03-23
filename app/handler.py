#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""App handler module exposing the webhook blueprint."""

from src.line_bot.handler import create_line_bot_handler

# 全局用戶偏好設置字典
# 結構: {user_id: "ja" | "en" | "multi"}
user_prefs = {}


def line_webhook_bp():
	"""Lazily create and return the LINE webhook blueprint."""
	return create_line_bot_handler(user_prefs)
