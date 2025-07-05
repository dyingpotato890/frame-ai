from urllib.parse import urlparse, parse_qs

def extract_video_id(url: str) -> str | None:
    """Extracts the video ID from a YouTube URL.
    Args:
        url (str): The YouTube URL.
    Returns:
        str: The video ID, or None if the URL is invalid or doesn't contain a video ID.
    """
    try:
        parsed_url = urlparse(url)
        youtube_domains = ['youtube.com', 'www.youtube.com', 'm.youtube.com', 'youtu.be']
        if parsed_url.netloc not in youtube_domains and \
           not any(domain in parsed_url.netloc for domain in ['youtube.com', 'youtu.be']):
            return None

        if parsed_url.path == '/watch':
            query_params = parse_qs(parsed_url.query)
            if 'v' in query_params:
                return query_params['v'][0]
        elif parsed_url.path.startswith('/embed/') or parsed_url.path.startswith('/shorts/'):
            return parsed_url.path.split('/')[-1]
        elif parsed_url.netloc == 'youtu.be':
            return parsed_url.path[1:]

    except Exception:
        return None

    return None