"""Download progress tracking for yt-dlp operations."""

from dataclasses import dataclass, field
from typing import Callable, Awaitable


@dataclass
class DownloadProgress:
    """Tracks the progress of a single download."""

    filename: str = ""
    status: str = "waiting"
    downloaded_bytes: int = 0
    total_bytes: int = 0
    speed: float = 0.0
    eta: int = 0

    @property
    def percentage(self) -> float:
        """Calculate download completion percentage."""
        if self.total_bytes <= 0:
            return 0.0
        return min((self.downloaded_bytes / self.total_bytes) * 100, 100.0)

    @property
    def speed_str(self) -> str:
        """Format download speed as a human-readable string."""
        if self.speed <= 0:
            return "N/A"
        if self.speed >= 1024 * 1024:
            return f"{self.speed / (1024 * 1024):.1f} MB/s"
        if self.speed >= 1024:
            return f"{self.speed / 1024:.1f} KB/s"
        return f"{self.speed:.0f} B/s"

    @property
    def eta_str(self) -> str:
        """Format ETA as HH:MM:SS."""
        if self.eta <= 0:
            return "N/A"
        hours, remainder = divmod(int(self.eta), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def format_progress_message(self, video_index: int = 0, total_videos: int = 0) -> str:
        """Format a progress message for display in Telegram.

        Args:
            video_index: Current video number (1-based).
            total_videos: Total number of videos.

        Returns:
            Formatted progress string.
        """
        lines = []
        if total_videos > 0:
            lines.append(f"📥 Downloading video {video_index}/{total_videos}")
        if self.filename:
            # Truncate long filenames
            name = self.filename[:50] + "..." if len(self.filename) > 50 else self.filename
            lines.append(f"📄 {name}")
        lines.append(f"⏳ Progress: {self.percentage:.0f}%")
        lines.append(f"🚀 Speed: {self.speed_str}")
        lines.append(f"⏱ ETA: {self.eta_str}")
        return "\n".join(lines)


def create_progress_hook(progress: DownloadProgress) -> Callable[[dict], None]:
    """Create a yt-dlp progress hook that updates a DownloadProgress instance.

    Args:
        progress: The DownloadProgress instance to update.

    Returns:
        A callback function compatible with yt-dlp's progress_hooks.
    """

    def hook(d: dict) -> None:
        progress.status = d.get("status", "unknown")
        progress.filename = d.get("filename", progress.filename)
        if progress.status == "downloading":
            progress.downloaded_bytes = d.get("downloaded_bytes", 0)
            progress.total_bytes = d.get("total_bytes") or d.get(
                "total_bytes_estimate", 0
            )
            progress.speed = d.get("speed") or 0.0
            progress.eta = d.get("eta") or 0
        elif progress.status == "finished":
            progress.downloaded_bytes = progress.total_bytes
            progress.speed = 0.0
            progress.eta = 0

    return hook
