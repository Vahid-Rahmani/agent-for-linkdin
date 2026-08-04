from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Message:
    id: int = 0
    sender_name: str = ""
    sender_profile: str = ""
    content: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    processed: bool = False
    ai_response: str = ""
    response_sent: bool = False
