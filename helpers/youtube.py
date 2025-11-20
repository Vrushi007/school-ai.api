import os
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class YouTubeHelper:
    """Helper class for YouTube Data API interactions"""
    
    def __init__(self):
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        self.base_url = "https://www.googleapis.com/youtube/v3"
        
        # Load allowed channels from environment variable
        allowed_channels_env = os.getenv('ALLOWED_CHANNELS', '')
        self.allowed_channels = []
        if allowed_channels_env:
            # Parse comma-separated channel IDs/names
            self.allowed_channels = [channel.strip() for channel in allowed_channels_env.split(',') if channel.strip()]
            logger.info(f"Loaded {len(self.allowed_channels)} allowed channels from environment")
        else:
            logger.info("No ALLOWED_CHANNELS configured - all channels will be included")
        
        if not self.api_key:
            logger.warning("YouTube API key not found. Set YOUTUBE_API_KEY environment variable.")
    
    def search_videos_by_keywords(self, keywords: List[str], 
                                max_results: int = 3,
                                video_duration: str = "medium",
                                video_category: str = "Education") -> Dict[str, Any]:
        """
        Search for YouTube videos using a list of keywords
        
        Args:
            keywords: List of search keywords
            max_results: Maximum number of videos to return per keyword (1-50)
            video_duration: 'short' (<4min), 'medium' (4-20min), 'long' (>20min), 'any'
            video_category: Filter by category (Education, Science, etc.)
            
        Returns:
            Dictionary with search results organized by keywords
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "YouTube API key not configured",
                "data": {}
            }
        
        results = {
            "success": True,
            "data": [],
            "total_videos": 0,
            "keywords_searched": keywords
        }
        all_videos = []
        
        for keyword in keywords:
            try:
                videos = self._search_single_keyword(
                    keyword=keyword,
                    max_results=max_results,
                    video_duration=video_duration,
                    video_category=video_category
                )

                all_videos.extend(videos)
                results["total_videos"] += len(videos)
                
                logger.info(f"Found {len(videos)} videos for keyword: {keyword}")
                
            except Exception as e:
                logger.error(f"Error searching for keyword '{keyword}': {str(e)}")
                results["data"].append({"keyword": keyword, "videos": []})
        results["data"] = all_videos
        return results
    
    def _search_single_keyword(self, keyword: str, max_results: int, 
                             video_duration: str, video_category: str) -> List[Dict[str, Any]]:
        """Search for videos with a single keyword"""
        
        # Build search query with educational focus
        search_query = f"{keyword} educational tutorial explanation"
        
        params = {
            'part': 'snippet',
            'q': search_query,
            'type': 'video',
            'maxResults': min(max_results, 50),  # API limit is 50
            'key': self.api_key,
            'order': 'relevance',
            'safeSearch': 'strict',
            'videoDefinition': 'high',
            'regionCode': 'US',
            'relevanceLanguage': 'en'
        }
        
        # Add duration filter if specified
        if video_duration != "any":
            params['videoDuration'] = video_duration
        
        # Add category filter if specified
        if video_category:
            params['videoCategoryId'] = self._get_category_id(video_category)
        
        response = requests.get(f"{self.base_url}/search", params=params)
        response.raise_for_status()
        
        data = response.json()
        videos = []
        
        for item in data.get('items', []):
            video_info = self._extract_video_info(item)
            if video_info:
                videos.append(video_info)
        
        return videos
    
    def _extract_video_info(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract relevant information from YouTube API response item"""
        try:
            snippet = item.get('snippet', {})
            video_id = item.get('id', {}).get('videoId')
            
            if not video_id:
                return None
            
            # Get additional video details
            video_details = self._get_video_details(video_id)
            
            return {
                'video_id': video_id,
                'title': snippet.get('title', ''),
                'description': snippet.get('description', '')[:200] + '...' if len(snippet.get('description', '')) > 200 else snippet.get('description', ''),
                'channel_title': snippet.get('channelTitle', ''),
                'channel_id': snippet.get('channelId', ''),
                'published_at': snippet.get('publishedAt', ''),
                'thumbnail_url': snippet.get('thumbnails', {}).get('medium', {}).get('url', ''),
                'video_url': f"https://www.youtube.com/watch?v={video_id}",
                'embed_url': f"https://www.youtube.com/embed/{video_id}",
                'duration': video_details.get('duration', 'Unknown'),
                'view_count': video_details.get('view_count', 'Unknown'),
                'like_count': video_details.get('like_count', 'Unknown')
            }
        except Exception as e:
            logger.error(f"Error extracting video info: {str(e)}")
            return None
    
    def _get_video_details(self, video_id: str) -> Dict[str, Any]:
        """Get additional video details like duration, views, likes"""
        try:
            params = {
                'part': 'contentDetails,statistics',
                'id': video_id,
                'key': self.api_key
            }
            
            response = requests.get(f"{self.base_url}/videos", params=params)
            response.raise_for_status()
            
            data = response.json()
            items = data.get('items', [])
            
            if not items:
                return {}
            
            item = items[0]
            content_details = item.get('contentDetails', {})
            statistics = item.get('statistics', {})
            
            # Parse ISO 8601 duration (PT4M13S) to readable format
            duration = content_details.get('duration', '')
            readable_duration = self._parse_duration(duration)
            
            return {
                'duration': readable_duration,
                'view_count': statistics.get('viewCount', '0'),
                'like_count': statistics.get('likeCount', '0'),
                'comment_count': statistics.get('commentCount', '0')
            }
            
        except Exception as e:
            logger.error(f"Error getting video details for {video_id}: {str(e)}")
            return {}
    
    def _parse_duration(self, iso_duration: str) -> str:
        """Convert ISO 8601 duration (PT4M13S) to readable format (4:13)"""
        try:
            import re
            
            if not iso_duration:
                return "Unknown"
            
            # Extract hours, minutes, seconds using regex
            pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
            match = re.match(pattern, iso_duration)
            
            if not match:
                return "Unknown"
            
            hours, minutes, seconds = match.groups()
            hours = int(hours) if hours else 0
            minutes = int(minutes) if minutes else 0
            seconds = int(seconds) if seconds else 0
            
            if hours > 0:
                return f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                return f"{minutes}:{seconds:02d}"
                
        except Exception:
            return "Unknown"
    
    def _get_category_id(self, category_name: str) -> str:
        """Get YouTube category ID by name"""
        categories = {
            'Education': '27',
            'Science & Technology': '28',
            'Howto & Style': '26',
            'Film & Animation': '1',
            'Autos & Vehicles': '2',
            'Music': '10',
            'Pets & Animals': '15',
            'Sports': '17',
            'Travel & Events': '19',
            'Gaming': '20',
            'People & Blogs': '22',
            'Comedy': '23',
            'Entertainment': '24',
            'News & Politics': '25',
            'Nonprofits & Activism': '29'
        }
        
        return categories.get(category_name, '27')  # Default to Education
    
    def get_educational_videos(self, subject: str, topic: str, 
                             class_level: str = None, max_results: int = 3) -> Dict[str, Any]:
        """
        Get educational videos for a specific subject and topic
        
        Args:
            subject: Subject name (e.g., "Physics", "Mathematics")
            topic: Specific topic (e.g., "Photosynthesis", "Quadratic Equations")
            class_level: Class/Grade level (e.g., "10th grade", "high school")
            max_results: Maximum number of videos to return
            
        Returns:
            Dictionary with curated educational video results
        """
        keywords = []
        
        # Build comprehensive search keywords
        base_keyword = f"{subject} {topic}"
        keywords.append(base_keyword)
        
        if class_level:
            keywords.append(f"{base_keyword} {class_level}")
            keywords.append(f"{topic} {class_level} {subject}")
        
        # Add educational modifiers
        keywords.append(f"{topic} explained")
        keywords.append(f"learn {topic}")
        
        # Search with educational focus
        results = self.search_videos_by_keywords(
            keywords=keywords[:3],  # Limit to top 3 keywords to avoid API quota issues
            max_results=max_results,
            video_duration="medium",  # 4-20 minutes is good for educational content
            video_category="Education"
        )
        
        # Flatten and deduplicate results
        all_videos = []
        seen_video_ids = set()
        
        for keyword_videos in results.get("data", {}).values():
            for video in keyword_videos:
                if video["video_id"] not in seen_video_ids:
                    all_videos.append(video)
                    seen_video_ids.add(video["video_id"])
        
        # Sort by relevance and view count
        all_videos.sort(key=lambda x: int(x.get("view_count", "0")), reverse=True)
        
        return {
            "success": True,
            "subject": subject,
            "topic": topic,
            "class_level": class_level,
            "videos": all_videos[:max_results],
            "total_found": len(all_videos)
        }

# Helper function for easy import
def get_youtube_videos_for_keywords(keywords: List[str], max_results: int = 3) -> Dict[str, Any]:
    """
    Simple function to get YouTube videos for a list of keywords
    
    Args:
        keywords: List of search keywords
        max_results: Maximum number of videos per keyword
        
    Returns:
        Dictionary with search results
    """
    youtube_helper = YouTubeHelper()
    return youtube_helper.search_videos_by_keywords(keywords, max_results)

def get_educational_videos_for_topic(subject: str, topic: str, 
                                   class_level: str = None, max_results: int = 3) -> Dict[str, Any]:
    """
    Simple function to get educational videos for a specific topic
    
    Args:
        subject: Subject name
        topic: Topic name
        class_level: Optional class level
        max_results: Maximum number of videos
        
    Returns:
        Dictionary with curated educational videos
    """
    youtube_helper = YouTubeHelper()
    return youtube_helper.get_educational_videos(subject, topic, class_level, max_results)