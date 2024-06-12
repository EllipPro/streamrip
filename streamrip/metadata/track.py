from __future__ import annotations

from collections import defaultdict
import logging
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum

from .album import AlbumMetadata
from .util import safe_get, typed

logger = logging.getLogger("streamrip")

class InvolvedPersonRoleType(Enum):
    Miscellaneous = 0
    Composer = 1
    Conductor = 2
    FeaturedArtist = 3
    Instruments = 4
    Lyricist = 5
    MainArtist = 6
    MixArtist = 7
    Producer = 8
    Publisher = 9
    Arranger = 10
    AandRDirector = 11
    AandR = 12
    AAndRAdministrator = 13
    AdditionalProduction = 14
    AHH = 15
    AssistantMixer = 16
    AssistantEngineer = 17
    AssistantProducer = 18
    AsstRecordingEngineer = 19
    AssociatedPerformer = 20
    Author = 21
    Choir = 22
    ChorusMaster = 23
    Contractor = 24
    CoProducer = 25
    Masterer = 26
    MiscProd = 27
    MusicProduction = 28
    PerformanceArranger = 29
    Programming = 30
    Programmer = 31
    RecordingEngineer = 32
    Soloist = 33
    StudioPersonnel = 34
    Vocals = 35
    Writer = 36
    BassGuitar = 37
    Cello = 38
    Drums = 39
    Guitar = 40
    Horn = 41
    Keyboards = 42
    Percussion = 43
    Piano = 44
    Trombone = 45
    Tuba = 46
    Trumpet = 47
    Viola = 48
    Violin = 49
    Orchestra = 50
    Engineer = 51
    MasteringEngineer = 52
    MixingEngineer = 53

class InvolvedPersonRoleMapping:
    RoleMappings = {
        InvolvedPersonRoleType.Miscellaneous: ["Miscellaneous"],
        InvolvedPersonRoleType.Composer: ["Composer", "Composer/r", "ComposerLyricist", "Composer-Lyricist"],
        InvolvedPersonRoleType.Conductor: ["Conductor", "Conductor/r"],
        InvolvedPersonRoleType.Engineer: ["Engineer"],
        InvolvedPersonRoleType.FeaturedArtist: ["FeaturedArtist", "Featuring", "featured-artist"],
        InvolvedPersonRoleType.Lyricist: ["Lyricist", "ComposerLyricist", "Composer-Lyricist"],
        InvolvedPersonRoleType.MainArtist: ["MainArtist", "main-artist", "Performer"],
        InvolvedPersonRoleType.MasteringEngineer: ["Mastering Engineer", "MasteringEngineer"],
        InvolvedPersonRoleType.MixArtist: ["Remixer", "Re-Mixer"],
        InvolvedPersonRoleType.MixingEngineer: ["Mixing Engineer", "RemixingEngineer", "Remixing Engineer"],
        InvolvedPersonRoleType.Orchestra: ["Orchestra", "Orchestra"],
        InvolvedPersonRoleType.Producer: ["Producer"],
        InvolvedPersonRoleType.Publisher: ["Publisher", "MusicPublisher"],
        InvolvedPersonRoleType.Arranger: ["Arranger"],
        InvolvedPersonRoleType.AandRDirector: ["AandRDirector"],
        InvolvedPersonRoleType.AandR: ["AandR"],
        InvolvedPersonRoleType.AAndRAdministrator: ["AAndRAdministrator"],
        InvolvedPersonRoleType.AdditionalProduction: ["AdditionalProduction"],
        InvolvedPersonRoleType.AHH: ["AHH"],
        InvolvedPersonRoleType.AssistantMixer: ["AssistantMixer"],
        InvolvedPersonRoleType.AssistantEngineer: ["AssistantEngineer"],
        InvolvedPersonRoleType.AssistantProducer: ["AssistantProducer"],
        InvolvedPersonRoleType.AsstRecordingEngineer: ["AsstRecordingEngineer"],
        InvolvedPersonRoleType.AssociatedPerformer: ["AssociatedPerformer"],
        InvolvedPersonRoleType.Author: ["Author"],
        InvolvedPersonRoleType.Choir: ["Choir"],
        InvolvedPersonRoleType.ChorusMaster: ["ChorusMaster"],
        InvolvedPersonRoleType.Contractor: ["Contractor"],
        InvolvedPersonRoleType.CoProducer: ["CoProducer"],
        InvolvedPersonRoleType.Masterer: ["Masterer"],
        InvolvedPersonRoleType.MiscProd: ["MiscProd"],
        InvolvedPersonRoleType.MusicProduction: ["MusicProduction"],
        InvolvedPersonRoleType.PerformanceArranger: ["PerformanceArranger"],
        InvolvedPersonRoleType.Programming: ["Programming"],
        InvolvedPersonRoleType.Programmer: ["Programmer"],
        InvolvedPersonRoleType.RecordingEngineer: ["RecordingEngineer"],
        InvolvedPersonRoleType.Soloist: ["Soloist"],
        InvolvedPersonRoleType.StudioPersonnel: ["StudioPersonnel"],
        InvolvedPersonRoleType.Vocals: ["Vocals"],
        InvolvedPersonRoleType.Writer: ["Writer"],
        InvolvedPersonRoleType.BassGuitar: ["BassGuitar"],
        InvolvedPersonRoleType.Cello: ["Cello"],
        InvolvedPersonRoleType.Drums: ["Drums"],
        InvolvedPersonRoleType.Guitar: ["Guitar"],
        InvolvedPersonRoleType.Horn: ["Horn"],
        InvolvedPersonRoleType.Keyboards: ["Keyboards"],
        InvolvedPersonRoleType.Percussion: ["Percussion"],
        InvolvedPersonRoleType.Piano: ["Piano"],
        InvolvedPersonRoleType.Trombone: ["Trombone"],
        InvolvedPersonRoleType.Tuba: ["Tuba"],
        InvolvedPersonRoleType.Trumpet: ["Trumpet"],
        InvolvedPersonRoleType.Viola: ["Viola"],
        InvolvedPersonRoleType.Violin: ["Violin"],
        InvolvedPersonRoleType.Orchestra: ["Orchestra"]
    }
    @staticmethod
    def get_strings_by_role(role: InvolvedPersonRoleType) -> List[str]:
        return InvolvedPersonRoleMapping.RoleMappings.get(role, [])

    @staticmethod
    def get_role_by_string(role_string: str) -> InvolvedPersonRoleType:
        for role, strings in InvolvedPersonRoleMapping.RoleMappings.items():
            if role_string in strings:
                return role
        return InvolvedPersonRoleType.Miscellaneous  # Default to Miscellaneous

class PerformersParser:
    def __init__(self, performers_full_string: str):
        self.performers = defaultdict(list)
        self.performers_full_string = performers_full_string

        if performers_full_string:
            for performer in performers_full_string.split(" - "):
                name, *roles = performer.split(', ')
                for role in roles:
                    role_enum = InvolvedPersonRoleMapping.get_role_by_string(role)
                    self.add_performer(name, role_enum)

    def add_performer(self, name: str, role: InvolvedPersonRoleType):
        self.performers[role].append(name)

    def get_performers_with_role(self, role: InvolvedPersonRoleType) -> List[str]:
        return self.performers.get(role, [])

    def get_specific_role(self, specific_role: str) -> List[str]:
        result = []
        for performer in self.performers_full_string.split(" - "):
            name, *roles = performer.split(', ')
            if specific_role in roles:
                result.append(name)
        return result

@dataclass(slots=True)
class TrackInfo:
    id: str
    quality: int

    bit_depth: Optional[int] = None
    explicit: bool = False
    sampling_rate: Optional[int | float] = None
    work: Optional[str] = None

@dataclass(slots=True)
class TrackMetadata:
    info: TrackInfo
    performers_full_string: str
    arranger: str
    lyricist: str
    conductor: str
    featured: str
    masteringengineer: str
    mixingengineer: str
    orchestra: str
    producer: str
    publisher: str
    vocals: str
    comment: str
    title: str
    album: AlbumMetadata
    artist: str
    tracknumber: int
    discnumber: int
    composer: str | None
    isrc: str | None = None

    @classmethod
    def from_qobuz(cls, album: AlbumMetadata, resp: dict) -> TrackMetadata | None:
        performers_full_string = resp.get("performers")
        parser = PerformersParser(performers_full_string)
        title = typed(resp["title"].strip(), str)
        isrc = typed(resp["isrc"], str)
        streamable = typed(resp.get("streamable", False), bool)
        if not streamable:
            return None

        version = typed(resp.get("version"), str | None)
        work = typed(resp.get("work"), str | None)
        if version is not None and version not in title:
            title = f"{title} ({version})"
        if work is not None and work not in title:
            title = f"{work}: {title}"

        arranger = parser.get_performers_with_role(InvolvedPersonRoleType.Arranger)
        arranger = ', '.join(arranger)
        composer = parser.get_performers_with_role(InvolvedPersonRoleType.Composer)
        if composer:
           composer = ', '.join(composer)
        else:
            composer = typed(resp.get("composer", {}).get("name"), str | None)
        tracknumber = typed(resp.get("track_number", 1), int)
        discnumber = typed(resp.get("media_number", 1), int)
        lyricist = parser.get_performers_with_role(InvolvedPersonRoleType.Lyricist)
        lyricist = ', '.join(lyricist)
        artist = parser.get_performers_with_role(InvolvedPersonRoleType.MainArtist)
        if artist:
            artist = ', '.join(artist)
        else:
            artist = typed(safe_get(resp, "performer", "name", ),str, )
        conductor = parser.get_performers_with_role(InvolvedPersonRoleType.Conductor)
        conductor = ', '.join(conductor)
        featured = parser.get_performers_with_role(InvolvedPersonRoleType.FeaturedArtist)
        featured = ', '.join(featured)
        if featured:
            title = f"{title} (feat. {featured})"
        masteringengineer = parser.get_performers_with_role(InvolvedPersonRoleType.MasteringEngineer)
        masteringengineer = ', '.join(masteringengineer)
        mixingengineer = parser.get_performers_with_role(InvolvedPersonRoleType.MixingEngineer)
        mixingengineer = ', '.join(mixingengineer)
        orchestra = parser.get_performers_with_role(InvolvedPersonRoleType.Orchestra)
        orchestra = ', '.join(orchestra)
        producer = parser.get_performers_with_role(InvolvedPersonRoleType.Producer)
        producer = ', '.join(producer)
        publisher = parser.get_performers_with_role(InvolvedPersonRoleType.Publisher)
        if publisher:
            publisher = ', '.join(publisher)
        else:
            publisher = album.label
        vocal = parser.get_performers_with_role(InvolvedPersonRoleType.Vocals)
        vocals = ', '.join(vocal)
        comment = resp.get("performers")
        track_id = str(resp["id"])
        bit_depth = typed(resp.get("maximum_bit_depth"), int | None)
        sampling_rate = typed(resp.get("maximum_sampling_rate"), int | float | None)
        # Is the info included?
        explicit = False

        info = TrackInfo(
            id=track_id,
            quality=album.info.quality,
            bit_depth=bit_depth,
            explicit=explicit,
            sampling_rate=sampling_rate,
            work=work,
        )
        return cls(
            info=info,
            performers_full_string=performers_full_string,
            arranger=arranger,
            lyricist=lyricist,
            conductor=conductor,
            featured=featured,
            masteringengineer=masteringengineer,
            mixingengineer=mixingengineer,
            orchestra=orchestra,
            producer=producer,
            publisher=publisher,
            vocals=vocals,
            comment=comment,
            title=title,
            album=album,
            artist=artist,
            tracknumber=tracknumber,
            discnumber=discnumber,
            composer=composer,
            isrc=isrc,
        )
    @classmethod
    def from_resp(cls, album: AlbumMetadata, source, resp) -> TrackMetadata | None:
        if source == "qobuz":
            return cls.from_qobuz(album, resp)

    def format_track_path(self, format_string: str) -> str:
        # Available keys: "tracknumber", "artist", "albumartist", "composer", "title",
        # and "explicit", "albumcomposer"
        none_text = "Unknown"
        info = {
            "title": self.title,
            "tracknumber": self.tracknumber,
            "artist": self.artist,
            "albumartist": self.album.albumartist,
            "albumcomposer": self.album.albumcomposer or none_text,
            "composer": self.composer or none_text,
            "explicit": " (Explicit) " if self.info.explicit else "",
        }
        return format_string.format(**info)