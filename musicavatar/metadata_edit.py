"""Editor de etiquetas REALES en archivos locales con Mutagen.

Admite campos título/artista/álbum/género y carátulas JPEG/PNG embebidas
para MP3, FLAC, M4A/MP4, OGG/OPUS y WAV, según admita cada contenedor.
Nunca edita el archivo en una importación o sugerencia automática.
"""
from __future__ import annotations
import base64
from pathlib import Path

WRITABLE_EXTENSIONS = {'.mp3', '.flac', '.m4a', '.mp4', '.ogg', '.oga', '.opus', '.wav', '.wma'}


def cover_mime(image_bytes: bytes) -> str:
    if image_bytes.startswith(b'\xff\xd8\xff'):
        return 'image/jpeg'
    if image_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'image/png'
    raise ValueError('La portada debe ser una imagen JPG o PNG válida.')


def write_file_tags(path: str | Path, title: str, artist: str, album: str,
                    genres: str, image_bytes: bytes | None = None) -> None:
    from mutagen import File as MutagenFile
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(str(source))
    if source.suffix.lower() not in WRITABLE_EXTENSIONS:
        raise ValueError('Este tipo de archivo no admite edición segura desde Musicavatar.')
    if not title.strip():
        raise ValueError('El título no puede estar vacío.')
    if image_bytes is not None and len(image_bytes) > 6 * 1024 * 1024:
        raise ValueError('La portada supera el límite de 6 MB.')
    mime = cover_mime(image_bytes) if image_bytes is not None else None
    if mime and source.suffix.lower() == '.wma':
        raise ValueError('Las portadas WMA/ASF no están soportadas para escritura. Cambia solo el texto.')

    # Primero verificamos que Mutagen pueda abrir este archivo para edición.
    easy = MutagenFile(str(source), easy=True)
    if easy is None:
        raise ValueError('Mutagen no reconoce etiquetas editables en este archivo.')
    if easy.tags is None:
        easy.add_tags()
    easy['title'] = [title.strip()]
    easy['artist'] = [artist.strip() or 'Artista desconocido']
    easy['album'] = [album.strip() or 'Álbum desconocido']
    if genres.strip():
        easy['genre'] = [g.strip() for g in genres.split(',') if g.strip()]
    elif 'genre' in easy:
        del easy['genre']
    easy.save()

    if image_bytes is None:
        return
    ext = source.suffix.lower()
    if ext == '.mp3':
        from mutagen.id3 import APIC, ID3
        tags = ID3(str(source))
        tags.delall('APIC')
        tags.add(APIC(encoding=3, mime=mime, type=3, desc='Cover', data=image_bytes))
        tags.save(str(source), v2_version=3)
    elif ext == '.wav':
        from mutagen.id3 import APIC
        raw = MutagenFile(str(source))
        if raw.tags is None:
            raw.add_tags()
        raw.tags.delall('APIC')
        raw.tags.add(APIC(encoding=3, mime=mime, type=3, desc='Cover', data=image_bytes))
        raw.save()
    elif ext == '.flac':
        from mutagen.flac import FLAC, Picture
        tags = FLAC(str(source))
        picture = Picture()
        picture.data = image_bytes
        picture.mime = mime
        picture.type = 3
        tags.clear_pictures()
        tags.add_picture(picture)
        tags.save()
    elif ext in ('.m4a', '.mp4'):
        from mutagen.mp4 import MP4, MP4Cover
        tags = MP4(str(source))
        fmt = MP4Cover.FORMAT_PNG if mime == 'image/png' else MP4Cover.FORMAT_JPEG
        tags['covr'] = [MP4Cover(image_bytes, imageformat=fmt)]
        tags.save()
    elif ext in ('.ogg', '.oga', '.opus'):
        from mutagen.flac import Picture
        raw = MutagenFile(str(source))
        picture = Picture()
        picture.data = image_bytes
        picture.mime = mime
        picture.type = 3
        raw['metadata_block_picture'] = [base64.b64encode(picture.write()).decode('ascii')]
        raw.save()
    else:
        raise ValueError('Los datos de texto se guardaron, pero este formato no admite portadas embebidas aquí.')


def safe_rename_audio(path: str | Path, new_title: str) -> Path:
    """Renombra el archivo conservando extensión; rechaza colisiones y nombres inválidos."""
    source = Path(path)
    invalid = '<>:"/\\|?*'
    name = ''.join('_' if c in invalid or ord(c) < 32 else c for c in new_title).strip(' .')
    if not name:
        raise ValueError('El nombre del archivo no puede quedar vacío.')
    if name.upper().split('.')[0] in {'CON','PRN','AUX','NUL',*(f'COM{i}' for i in range(1,10)),*(f'LPT{i}' for i in range(1,10))}:
        raise ValueError('Ese nombre está reservado por Windows.')
    new = source.with_name(name + source.suffix)
    if new == source:
        return source
    if new.exists() and new.resolve() != source.resolve():
        raise FileExistsError('Ya hay un archivo con ese nombre en la carpeta.')
    source.rename(new)
    return new
