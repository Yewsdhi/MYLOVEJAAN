"""Startup prewarm for the first /play after a restart.

Why this exists
---------------
On a fresh Heroku restart, the very first /play call used to take 3–4 minutes
because several expensive resources were lazily initialised *on that first
request* rather than during startup:

1. The SHRUTI download API (api.shrutibots.site) — used by download_song() /
   download_video() in platforms/Youtube.py. The worker goes to sleep when
   idle; the first call after a restart hits a cold worker and the aiohttp
   client has a 120s total timeout. That alone can eat 1–2 minutes.
2. py_yt.VideosSearch — first call has to import the package, build an
   aiohttp.ClientSession, and fetch the YouTube search HTML. ~0.5–2s, but
   it stacks on top of everything else.
3. yt-dlp YoutubeDL — import is ~0.8s and the first YoutubeDL() instantiation
   loads extractors. Happens lazily when autoplay.py or Youtube.py first
   calls it.
4. i.ytimg.com thumbnail fetch — first call resolves DNS + opens TLS.

This module fires off best-effort prewarm tasks *during* bot startup so that
by the time the first /play arrives, all of these are already warm. Every
prewarm is wrapped in try/except and runs concurrently — a failure in any
one of them never blocks startup and never breaks playback; the only effect
is that the first /play falls back to the original cold path for that
particular resource.
"""

import asyncio

from ..logging import LOGGER


async def _prewarm_shruti_api():
    """Wake up the SHRUTI download API worker so the first real /play
    doesn't pay the cold-start penalty. We don't care about the response
    body — we just want the worker alive."""
    try:
        import os
        import aiohttp
        api_url = os.environ.get("SHRUTI_API_URL", "https://api.shrutibots.site")
        api_key = os.environ.get("SHRUTI_API_KEY", "")
        # Use a short timeout — we only want to nudge the worker awake.
        # If it doesn't respond in 10s, the first /play will pay the cold
        # start anyway; no point blocking startup longer than that.
        timeout = aiohttp.ClientTimeout(total=10)
        params = {"url": "dQw4w9WgXcQ", "type": "audio"}
        if api_key:
            params["api_key"] = api_key
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                async with session.get(f"{api_url}/download",
                                       params=params) as resp:
                    # Drain the body so the connection is reused.
                    await resp.read()
            except Exception:
                pass
        LOGGER(__name__).info("𝗦𝗛𝗥𝗨𝗧𝗜 𝗔𝗣𝗜 𝗣𝗥𝗘𝗪𝗔𝗥𝗠 𝗗𝗢𝗡𝗘")
    except Exception as e:
        # Best-effort; never fail startup over a prewarm.
        LOGGER(__name__).warning(f"Shruti API prewarm skipped: {type(e).__name__}")


async def _prewarm_py_yt_search():
    """Force py_yt import + first VideosSearch.next() so the first real
    /play doesn't pay the import + first-HTTP-session cost inline."""
    try:
        from py_yt import VideosSearch
        search = VideosSearch("warmup", limit=1)
        await search.next()
        LOGGER(__name__).info("𝗣𝗬_𝗬𝗧 𝗦𝗘𝗔𝗥𝗖𝗛 𝗣𝗥𝗘𝗪𝗔𝗥𝗠 𝗗𝗢𝗡𝗘")
    except Exception as e:
        LOGGER(__name__).warning(f"py_yt prewarm skipped: {type(e).__name__}")


async def _prewarm_yt_dlp():
    """Force yt-dlp import + YoutubeDL instantiation so the first real
    extract_info() call doesn't pay the import cost inline. We do NOT
    make a real network call here — just instantiation loads the
    extractors and gets the YoutubeDL object ready."""
    try:
        import yt_dlp
        # Instantiation loads extractors and validates the module. We
        # intentionally don't call extract_info() here because that would
        # be a real YouTube request (and we don't want to hit YouTube
        # at startup just for warmth).
        _ = yt_dlp.YoutubeDL({
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "extract_flat": True,
        })
        LOGGER(__name__).info("𝗬𝗧-𝗗𝗟𝗣 𝗣𝗥𝗘𝗪𝗔𝗥𝗠 𝗗𝗢𝗡𝗘")
    except Exception as e:
        LOGGER(__name__).warning(f"yt-dlp prewarm skipped: {type(e).__name__}")


async def _prewarm_ytimg():
    """Resolve DNS + open TLS to i.ytimg.com so the first thumbnail fetch
    in get_thumb() doesn't pay the cold DNS/TLS cost."""
    try:
        import aiohttp
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                async with session.get(
                    "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg"
                ) as resp:
                    await resp.read()
            except Exception:
                pass
        LOGGER(__name__).info("𝗜.𝗬𝗧𝗜𝗠𝗚 𝗣𝗥𝗘𝗪𝗔𝗥𝗠 𝗗𝗢𝗡𝗘")
    except Exception as e:
        LOGGER(__name__).warning(f"i.ytimg prewarm skipped: {type(e).__name__}")


async def prewarm_all():
    """Run all prewarm tasks concurrently. Each is best-effort and
    independent — a failure in one never blocks the others. Total wall
    time is bounded by the slowest task (max ~10s for the SHRUTI nudge).
    """
    await asyncio.gather(
        _prewarm_shruti_api(),
        _prewarm_py_yt_search(),
        _prewarm_yt_dlp(),
        _prewarm_ytimg(),
        return_exceptions=True,
    )
    LOGGER(__name__).info("𝗔𝗟𝗟 𝗣𝗥𝗘𝗪𝗔𝗥𝗠 𝗧𝗔𝗦𝗞𝗦 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘𝗗")
