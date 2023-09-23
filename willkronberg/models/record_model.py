from typing import List, Optional

from pydantic import BaseModel

from willkronberg.models.discogs_model import Artist


class RecordRelease(BaseModel):
    id: int
    date_added: str
    artists: List[Artist]
    title: str
    cover_image: str
    year: int
    url: Optional[str]
