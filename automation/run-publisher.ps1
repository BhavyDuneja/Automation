# Publishes approved, due posts from content\queue. Pure Python, no AI usage.
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
python scripts\publish_queue.py
