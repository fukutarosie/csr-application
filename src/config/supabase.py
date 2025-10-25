"""DEPRECATED: Supabase configuration has been moved to src/entity/supabase_config.py

This file is kept for backwards compatibility.
New code should import from: src.entity.supabase_config
"""
from src.entity.supabase_config import get_supabase, supabase, SUPABASE_KEY, SUPABASE_URL

__all__ = ['get_supabase', 'supabase', 'SUPABASE_KEY', 'SUPABASE_URL']