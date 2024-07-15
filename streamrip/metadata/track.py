from __future__ import annotations
import unicodedata
from collections import defaultdict
import logging
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum

from .album import AlbumMetadata
from .util import safe_get, typed


# Assuming AlbumMetadata and safe_get are imported correctly
# from .album import AlbumMetadata
# from .util import safe_get, typed

logger = logging.getLogger("streamrip")

class InvolvedPersonRoleType(Enum):
    Miscellaneous = 0
    Composer = 1
    Conductor = 2
    FeaturedArtist = 3
    Lyricist = 4
    MainArtist = 5
    MixingEngineer = 6
    Producer = 7
    Publisher = 8
    Arranger = 9
    AandRDirector = 10
    AandR = 11
    AAndRAdministrator = 12
    AdditionalProduction = 13
    AHH = 14
    AssistantMixer = 15
    AssistantEngineer = 16
    AssistantProducer = 17
    AsstRecordingEngineer = 18
    AssociatedPerformer = 19
    Author = 20
    Choir = 21
    ChorusMaster = 22
    Contractor = 23
    CoProducer = 24
    Masterer = 25
    MiscProd = 26
    MusicProduction = 27
    PerformanceArranger = 28
    Programming = 29
    Programmer = 30
    RecordingEngineer = 31
    Soloist = 32
    StudioPersonnel = 33
    Vocals = 34
    Writer = 35
    BassGuitar = 36
    Cello = 37
    Drums = 38
    Guitar = 39
    Horn = 40
    Keyboards = 41
    Percussion = 42
    Piano = 43
    Trombone = 44
    Tuba = 45
    Trumpet = 46
    Viola = 47
    Violin = 48
    Orchestra = 49
    Engineer = 50
    MasteringEngineer = 51
    Voice = 52
    Accordion = 53
    ClassicalGuitar = 54
    DoubleBass = 55
    VibraHarp = 56

class InvolvedPersonRoleMapping:
    RoleMappings = {
        InvolvedPersonRoleType.Miscellaneous: ["Miscellaneous"],
        InvolvedPersonRoleType.Composer: ["Composer", "Composer\r", "ComposerLyricist", "Composer-Lyricist"],
        InvolvedPersonRoleType.Conductor: ["Conductor", "Conductor\r"],
        InvolvedPersonRoleType.Engineer: ["Engineer"],
        InvolvedPersonRoleType.FeaturedArtist: ["FeaturedArtist", "Featuring", "featured-artist"],
        InvolvedPersonRoleType.Lyricist: ["Lyricist", "Lyricist\r", "ComposerLyricist", "Composer-Lyricist"],
        InvolvedPersonRoleType.MainArtist: ["MainArtist", "Main Artist", "Main Artist\r", "main-artist", "Performer"],
        InvolvedPersonRoleType.MasteringEngineer: ["Mastering Engineer", "MasteringEngineer"],
        InvolvedPersonRoleType.MixingEngineer: ["Mixing Engineer", "Mixing Engineer\r", "Remixing Engineer", "RemixingEngineer", "Remixer", "Re-Mixer"],
        InvolvedPersonRoleType.Orchestra: ["Orchestra"],
        InvolvedPersonRoleType.Producer: ["Producer", "Producer\r"],
        InvolvedPersonRoleType.Publisher: ["Publisher", "MusicPublisher"],
        InvolvedPersonRoleType.Arranger: ["Arranger", "MusicArranger"],
        InvolvedPersonRoleType.AandRDirector: ["A&RDirector", "A&R Director"],
        InvolvedPersonRoleType.AandR: ["A&R"],
        InvolvedPersonRoleType.AAndRAdministrator: ["A&RAdministrator", "A&R Administrator"],
        InvolvedPersonRoleType.AdditionalProduction: ["AdditionalProduction", "Additional Production"],
        InvolvedPersonRoleType.AHH: ["AHH"],
        InvolvedPersonRoleType.AssistantMixer: ["AssistantMixer", "Assistant Mixer"],
        InvolvedPersonRoleType.AssistantEngineer: ["AssistantEngineer", "Assistant Engineer"],
        InvolvedPersonRoleType.AssistantProducer: ["AssistantProducer", "Assistant Producer"],
        InvolvedPersonRoleType.AsstRecordingEngineer: ["AsstRecordingEngineer", "Asst Recording Engineer"],
        InvolvedPersonRoleType.AssociatedPerformer: ["AssociatedPerformer", "Associated Performer"],
        InvolvedPersonRoleType.Author: ["Author"],
        InvolvedPersonRoleType.Choir: ["Choir"],
        InvolvedPersonRoleType.ChorusMaster: ["ChorusMaster", "Chorus Master"],
        InvolvedPersonRoleType.Contractor: ["Contractor"],
        InvolvedPersonRoleType.CoProducer: ["CoProducer"],
        InvolvedPersonRoleType.Masterer: ["Masterer"],
        InvolvedPersonRoleType.MiscProd: ["MiscProd"],
        InvolvedPersonRoleType.MusicProduction: ["MusicProduction", "Music Production"],
        InvolvedPersonRoleType.PerformanceArranger: ["PerformanceArranger", "Performance Arranger"],
        InvolvedPersonRoleType.Programming: ["Programming"],
        InvolvedPersonRoleType.Programmer: ["Programmer"],
        InvolvedPersonRoleType.RecordingEngineer: ["RecordingEngineer", "Recording Engineer"],
        InvolvedPersonRoleType.Soloist: ["Soloist"],
        InvolvedPersonRoleType.StudioPersonnel: ["StudioPersonnel", "Studio Personnel"],
        InvolvedPersonRoleType.Vocals: ["Vocals"],
        InvolvedPersonRoleType.Writer: ["Writer"],
        InvolvedPersonRoleType.BassGuitar: ["BassGuitar", "Bass Guitar"],
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
        InvolvedPersonRoleType.Voice: ["Voice"],
        InvolvedPersonRoleType.Accordion: ["Accordion"],
        InvolvedPersonRoleType.ClassicalGuitar: ["ClassicalGuitar", "Classical Guitar"],
        InvolvedPersonRoleType.DoubleBass: ["DoubleBass", "Double Bass"],
        InvolvedPersonRoleType.VibraHarp: ["VibraHarp", "Vibra Harp"],
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
        self._parse_performers()

    def _parse_performers(self):
        if self.performers_full_string:
            for performer in self.performers_full_string.split(" - "):
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
    ahh: str
    assistantmixer: str
    assistantengineer: str
    assistantproducer: str
    asstrecordingengineer: str
    associatedperformer: str
    author: str
    choir: str
    chorusmaster: str
    contractor: str
    coproducer: str
    masterer: str
    miscprod: str
    musicproduction: str
    performancearranger: str
    programming: str
    recordingengineer: str
    soloist: str
    studiopersonnel: str
    bassguitar: str
    cello: str
    drums: str
    guitar: str
    horn: str
    keyboards: str
    percussion: str
    piano: str
    trombone: str
    tuba: str
    trumpet: str
    viola: str
    violin: str
    engineer: str
    accordion: str
    classicalguitar: str
    doublebass: str
    vibraharp: str
    lyricist: str
    conductor: str
    featured: str
    masteringengineer: str
    mixingengineer: str
    orchestra: str
    producer: str
    programmer: str
    publisher: str
    vocals: str
    voice: str
    writer: str
    comment: str
    title: str
    album: AlbumMetadata
    artist: str
    tracknumber: int
    discnumber: int
    composer:  str | None
    artist_path: str | None = None
    composer_path: str | None = None
    isrc: Optional[str] = None

    @classmethod
    def from_qobuz(cls, album: AlbumMetadata, resp: dict) -> TrackMetadata | None:
        performers_full_string = resp.get("performers")
        comment = resp.get("performers")
        parser = PerformersParser(performers_full_string)
        title = typed(resp["title"].strip(), str)
        isrc = typed(resp["isrc"], str)
        streamable = typed(resp.get("streamable", False), bool)
        if not streamable:
            return None

        version = typed(resp.get("version"), str | None)
        work = typed(resp.get("work"), str | None)
        title = cls._append_version_and_work(title, version, work)

        arranger = parser.get_performers_with_role(InvolvedPersonRoleType.Arranger)
        ahh = parser.get_performers_with_role(InvolvedPersonRoleType.AHH)
        assistantmixer = parser.get_performers_with_role(InvolvedPersonRoleType.AssistantMixer)
        assistantengineer = parser.get_performers_with_role(InvolvedPersonRoleType.AssistantEngineer)
        assistantproducer = parser.get_performers_with_role(InvolvedPersonRoleType.AssistantProducer)
        asstrecordingengineer = parser.get_performers_with_role(InvolvedPersonRoleType.AsstRecordingEngineer)
        associatedperformer = parser.get_performers_with_role(InvolvedPersonRoleType.AssociatedPerformer)
        author = parser.get_performers_with_role(InvolvedPersonRoleType.Author)
        choir = parser.get_performers_with_role(InvolvedPersonRoleType.Choir)
        chorusmaster = parser.get_performers_with_role(InvolvedPersonRoleType.ChorusMaster)
        contractor = parser.get_performers_with_role(InvolvedPersonRoleType.Contractor)
        coproducer = parser.get_performers_with_role(InvolvedPersonRoleType.CoProducer)
        masterer = parser.get_performers_with_role(InvolvedPersonRoleType.Masterer)
        miscprod = parser.get_performers_with_role(InvolvedPersonRoleType.MiscProd)
        musicproduction = parser.get_performers_with_role(InvolvedPersonRoleType.MusicProduction)
        performancearranger = parser.get_performers_with_role(InvolvedPersonRoleType.PerformanceArranger)
        programming = parser.get_performers_with_role(InvolvedPersonRoleType.Programming)
        recordingengineer = parser.get_performers_with_role(InvolvedPersonRoleType.RecordingEngineer)
        soloist = parser.get_performers_with_role(InvolvedPersonRoleType.Soloist)
        studiopersonnel = parser.get_performers_with_role(InvolvedPersonRoleType.StudioPersonnel)
        bassguitar = parser.get_performers_with_role(InvolvedPersonRoleType.BassGuitar)
        cello = parser.get_performers_with_role(InvolvedPersonRoleType.Cello)
        drums = parser.get_performers_with_role(InvolvedPersonRoleType.Drums)
        guitar = parser.get_performers_with_role(InvolvedPersonRoleType.Guitar)
        horn = parser.get_performers_with_role(InvolvedPersonRoleType.Horn)
        keyboards = parser.get_performers_with_role(InvolvedPersonRoleType.Keyboards)
        percussion = parser.get_performers_with_role(InvolvedPersonRoleType.Percussion)
        piano = parser.get_performers_with_role(InvolvedPersonRoleType.Piano)
        trombone = parser.get_performers_with_role(InvolvedPersonRoleType.Trombone)
        tuba = parser.get_performers_with_role(InvolvedPersonRoleType.Tuba)
        trumpet = parser.get_performers_with_role(InvolvedPersonRoleType.Trumpet)
        viola = parser.get_performers_with_role(InvolvedPersonRoleType.Viola)
        violin = parser.get_performers_with_role(InvolvedPersonRoleType.Violin)
        orchestra = parser.get_performers_with_role(InvolvedPersonRoleType.Orchestra)
        engineer = parser.get_performers_with_role(InvolvedPersonRoleType.Engineer)
        accordion = parser.get_performers_with_role(InvolvedPersonRoleType.Accordion)
        classicalguitar = parser.get_performers_with_role(InvolvedPersonRoleType.ClassicalGuitar)
        doublebass = parser.get_performers_with_role(InvolvedPersonRoleType.DoubleBass)
        vibraharp = parser.get_performers_with_role(InvolvedPersonRoleType.VibraHarp)


        composer = cls._get_composer(resp, parser)
        if composer:
            composer_path = ', '.join(composer)
        else:
            composer_path = None

        tracknumber = typed(resp.get("track_number", 1), int)
        discnumber = typed(resp.get("media_number", 1), int)
        lyricist = parser.get_performers_with_role(InvolvedPersonRoleType.Lyricist)

        artists =  cls._get_artist(resp, parser)
        if artists:
            artist_path = ', '.join(artists)
        else:
            artist_path = None
        
        conductor = parser.get_performers_with_role(InvolvedPersonRoleType.Conductor)
        featured = parser.get_performers_with_role(InvolvedPersonRoleType.FeaturedArtist)
        masteringengineer = parser.get_performers_with_role(InvolvedPersonRoleType.MasteringEngineer)
        mixingengineer = parser.get_performers_with_role(InvolvedPersonRoleType.MixingEngineer)
        orchestra = parser.get_performers_with_role(InvolvedPersonRoleType.Orchestra)
        producer = parser.get_performers_with_role(InvolvedPersonRoleType.Producer)
        programmer = parser.get_performers_with_role(InvolvedPersonRoleType.Programmer)
        publisher = album.label
        vocals = parser.get_performers_with_role(InvolvedPersonRoleType.Vocals)
        voice = parser.get_performers_with_role(InvolvedPersonRoleType.Voice)
        writer = parser.get_performers_with_role(InvolvedPersonRoleType.Writer)
        comment = resp.get("performers")
        track_id = str(resp["id"])
        bit_depth = typed(resp.get("maximum_bit_depth"), int | None)
        sampling_rate = typed(resp.get("maximum_sampling_rate"), int | float | None)
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
            ahh=ahh,
            assistantmixer=assistantmixer,
            assistantengineer=assistantengineer,
            assistantproducer=assistantproducer,
            asstrecordingengineer=asstrecordingengineer,
            associatedperformer=associatedperformer,
            author=author,
            choir=choir,
            chorusmaster=chorusmaster,
            contractor=contractor,
            coproducer=coproducer,
            masterer=masterer,
            miscprod=miscprod,
            musicproduction=musicproduction,
            performancearranger=performancearranger,
            programming=programming,
            recordingengineer=recordingengineer,
            soloist=soloist,
            studiopersonnel=studiopersonnel,
            bassguitar=bassguitar,
            cello=cello,
            drums=drums,
            guitar=guitar,
            horn=horn,
            keyboards=keyboards,
            percussion=percussion,
            piano=piano,
            trombone=trombone,
            tuba=tuba,
            trumpet=trumpet,
            viola=viola,
            violin=violin,
            engineer=engineer,
            accordion=accordion,
            classicalguitar=classicalguitar,
            doublebass=doublebass,
            vibraharp=vibraharp,
            lyricist=lyricist,
            conductor=conductor,
            featured=featured,
            masteringengineer=masteringengineer,
            mixingengineer=mixingengineer,
            orchestra=orchestra,
            producer=producer,
            programmer=programmer,
            publisher=publisher,
            vocals=vocals,
            voice=voice,
            writer=writer,
            comment=comment,
            title=title,
            album=album,
            artist=artists,
            tracknumber=tracknumber,
            discnumber=discnumber,
            composer=composer,
            isrc=isrc,
            artist_path=artist_path,
            composer_path=composer_path
        )

    @classmethod
    def from_resp(cls, album: AlbumMetadata, source, resp) -> TrackMetadata | None:
        if source == "qobuz":
            return cls.from_qobuz(album, resp)
        
    @staticmethod
    def _append_version_and_work(title: str, version: Optional[str], work: Optional[str]) -> str:
        if version and version not in title:
            title = f"{title} ({version})"
        if work and work not in title:
            title = f"{work}: {title}"
        return title

    @staticmethod
    def _get_composer(resp: dict, parser: PerformersParser) -> str | None:
        composer = parser.get_performers_with_role(InvolvedPersonRoleType.Composer)
        composer2 = typed(resp.get("composer", {}).get("name"), str | None)
        if composer:
            return composer
        elif composer2:
            return composer2
        else:
            return None

    @staticmethod
    def _get_artist(resp: dict, parser: PerformersParser) -> list:
        album_data = resp['album']
        main_artist = resp.get('performer', album_data['artist'])
        artists = [
            unicodedata.normalize('NFKD', main_artist['name'])
            .encode('ascii', 'ignore')
            .decode('utf-8')
        ]
        if resp.get('performers'):
            performers = []
            for credit in resp['performers'].split(' - '):
                contributor_role = credit.split(', ')[1:]
                contributor_name = credit.split(', ')[0]

                for contributor in ["MainArtist", "Main Artist", "Main Artist\r", "main-artist", "Performer", "Primary"]:
                    if contributor in contributor_role:
                        if contributor_name not in artists:
                            artists.append(contributor_name)
                if not contributor_role:
                    continue
                performers.append(f"{contributor_name}, {', '.join(contributor_role)}")
            resp['performers'] = ' - '.join(performers)
            artists = [artist for artist in artists if artist != ""]
        if artists:
            return artists
        return typed(safe_get(resp, "performer", "name"), str)


    def format_track_path(self, format_string: str) -> str:
        none_text = "Unknown"
        info = {
            "title": self.title,
            "tracknumber": self.tracknumber,
            "artist": self.artist_path,
            "albumartist": self.album.albumartist,
            "albumcomposer": self.album.albumcomposer or none_text,
            "composer": self.composer_path or none_text,
            "explicit": " (Explicit) " if self.info.explicit else "",
        }
        return format_string.format(**info)