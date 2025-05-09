import yt_dlp

class DownloadYoutubeVideo:
    def __init__(self, url : str, quality: str="bestvideo+bestaudio/best", format_output: str="mkv"):
        self.url = url
        self.kwargs = {
            "format": quality,
            "merge_output_format": format_output
        }

    def download_video(self):
        video = yt_dlp.YoutubeDL(self.kwargs)
        video.download([self.url])


