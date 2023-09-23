from typing import List, Optional

from pydantic import BaseModel


class PaginationResponseUrls(BaseModel):
    next: Optional[str] = None
    last: Optional[str] = None


class PaginationResponse(BaseModel):
    items: int
    page: int
    pages: int
    per_page: int
    urls: PaginationResponseUrls


class ReleaseInstanceNote(BaseModel):
    field_id: int
    value: str


class Format(BaseModel):
    name: str
    qty: str
    text: Optional[str] = None
    descriptions: Optional[List[str]] = None


class Label(BaseModel):
    name: str
    catno: str
    entity_type: str
    entity_type_name: str
    id: int
    resource_url: str


class Artist(BaseModel):
    name: str
    anv: str
    join: str
    role: str
    tracks: str
    id: int
    resource_url: str


class Release(BaseModel):
    id: int
    master_id: int
    master_url: Optional[str] = None
    resource_url: str
    thumb: str
    cover_image: str
    title: str
    year: int
    formats: List[Format]
    labels: List[Label]
    artists: List[Artist]
    genres: List[str]
    styles: List[str]


class ReleaseInstance(BaseModel):
    id: int
    instance_id: int
    date_added: str
    rating: int
    folder_id: int
    notes: Optional[List[ReleaseInstanceNote]] = None
    basic_information: Release


class GetCollectionPaginatedResponse(BaseModel):
    releases: List[ReleaseInstance]
    pagination: PaginationResponse
