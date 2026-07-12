#!/usr/bin/env python3
"""Cron entry point: python3 scheduler/daily_scan.py"""
from agents.security_agent import SecurityBarbie
for result in SecurityBarbie().run_daily():print(f"{result.run_id} {result.target} {result.status}")
