from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Post:
    id: int = 0
    post_url: str = ""
    author_name: str = ""
    content: str = ""
    likes: int = 0
    comments_count: int = 0
    shares: int = 0
    impressions: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
