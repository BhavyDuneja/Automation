# Publishes approved, due posts from content\queue and approved articles from content\blog. Pure Python, no AI usage.
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
python scripts\publish_queue.py
python scripts\publish_blog.py
