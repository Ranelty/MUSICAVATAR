"""Capas y opciones del avatar chibi de Musicavatar.

La imagen se construye en 64×64 píxeles con QPainter. Cada prenda se pinta
independientemente para no crear combinaciones de sprites pre-renderizados.
Este módulo evita cargar texturas de alta resolución o imágenes de terceros.
"""
from __future__ import annotations
from dataclasses import dataclass

HAIR_COLORS = (
    ('Castaño', '#a65d3b'), ('Negro', '#34303e'), ('Lila', '#8d72bf'),
    ('Rubio', '#e0b46e'), ('Rosa', '#ca839c'), ('Blanco', '#ded9de'),
)
OUTFIT_COLORS = (
    ('Azul', '#4b6998'), ('Morado', '#71549d'), ('Blanco', '#dddddf'),
    ('Verde', '#4c8a72'), ('Rosa', '#af6587'), ('Negro', '#48404c'),
)
HAIR_STYLES = (('Corto', 'short'), ('Despeinado', 'messy'), ('Largo', 'long'))
TOP_STYLES = (('Camiseta', 'tshirt'), ('Camisa', 'shirt'), ('Sudadera', 'hoodie'))
PANTS = (('Negro', '#35313b'), ('Mezclilla', '#395c85'), ('Beige', '#b79270'))
SHOES = (('Tenis blancos', 'white'), ('Tenis rojos', 'red'), ('Botas oscuras', 'boots'))
SKIN_TONES = (('Claro', '#f4d0aa'), ('Medio', '#ca936e'), ('Oscuro', '#845846'))
PRESENTATIONS = (('Masculino', 'masculine'), ('Femenino', 'feminine'), ('Neutro', 'neutral'))
ACCESSORIES = ('Auriculares', 'Gorra', 'Moño', 'Ninguno')


def _values(options):
    return {value for _, value in options}


@dataclass(frozen=True)
class AvatarLook:
    hair: str = '#8d72bf'  # conservamos el color por defecto de la v0.4
    outfit: str = '#71549d'
    accessory: str = 'Auriculares'
    hair_style: str = 'short'
    top_style: str = 'hoodie'
    pants: str = '#35313b'
    shoes: str = 'white'
    skin: str = '#f4d0aa'
    presentation: str = 'neutral'

    def validated(self) -> 'AvatarLook':
        """No usar valores guardados desconocidos en el dibujado."""
        defaults = AvatarLook()
        allowed = {
            'hair': _values(HAIR_COLORS) | {'#6d4b47', '#608dbb', '#383846'},  # v0.4
            'outfit': _values(OUTFIT_COLORS),
            'accessory': set(ACCESSORIES),
            'hair_style': _values(HAIR_STYLES),
            'top_style': _values(TOP_STYLES),
            'pants': _values(PANTS),
            'shoes': _values(SHOES),
            'skin': _values(SKIN_TONES),
            'presentation': _values(PRESENTATIONS),
        }
        return AvatarLook(**{
            key: getattr(self, key) if getattr(self, key) in values else getattr(defaults, key)
            for key, values in allowed.items()
        })


def draw_character(painter, x: int, y: int, look: AvatarLook,
                   mood: str, playing: bool, tick: int, glow: str):
    """Pinta al personaje por capas. Usa solo rectángulos (pixel art real)."""
    from PySide6.QtGui import QColor
    L = look.validated()
    dark = '#19151c'
    hair, top, pants, skin = L.hair, L.outfit, L.pants, L.skin
    def r(dx, dy, w, h, col):
        painter.fillRect(x + dx, y + dy, w, h, QColor(col))
    def highlight(color, amt=126):
        return QColor(color).lighter(amt).name()
    def shade(color, amt=76):
        return QColor(color).darker(round(10000/amt)).name()

    # Sombra detrás del personaje; movimiento de 1 píxel con la música.
    r(-12, 29, 26, 2, '#302837')
    # Pelo detrás de la cara. El estilo largo es una silueta distinta.
    if L.hair_style == 'long':
        r(-12, -3, 25, 23, dark)
        r(-11, -3, 23, 23, hair)
        r(-11, 9, 6, 13, shade(hair))
        r(7, 9, 6, 13, shade(hair))
    elif L.hair_style == 'messy':
        r(-11, -8, 24, 11, dark)
        for a,b,w,h in [(-13,-5,6,5),(-8,-11,6,6),(-1,-12,7,7),(7,-9,6,7),(12,-5,3,5)]:
            r(a,b,w,h,dark)
        r(-10,-7,21,9,hair)
        r(-12,-4,5,5,hair)
        r(-7,-10,5,5,hair)
        r(0,-11,6,6,hair)
        r(8,-8,4,7,hair)
    else:
        r(-12,-7,25,17,dark)
        r(-11,-6,23,15,hair)
        r(-9,-9,18,5,dark)
        r(-8,-8,16,6,hair)

    # Piernas / pantalones, silueta definida y cambiable.
    r(-10, 19, 21, 10, dark)
    r(-9, 20, 8, 9, pants)
    r(2, 20, 8, 9, pants)
    r(-8, 20, 4, 3, highlight(pants, 115))
    r(3, 20, 4, 3, highlight(pants, 115))
    # Zapatos: diferentes siluetas y paletas.
    shoe_main = {'white':'#e4e0df', 'red':'#b45152', 'boots':'#38343b'}[L.shoes]
    shoe_shine = {'white':'#faf5f0', 'red':'#e4b5a9', 'boots':'#6a5862'}[L.shoes]
    for sx in (-11, 1):
        r(sx, 27, 12, 5, dark)
        r(sx+1, 27, 9, 3 if L.shoes != 'boots' else 4, shoe_main)
        r(sx+2, 28, 3, 1, shoe_shine)
        r(sx+1, 31, 11, 1, '#ece6e6' if L.shoes != 'boots' else '#252128')

    # Parte superior y manos, en capas separadas de pantalones/calzado.
    r(-12, 9, 25, 16, dark)
    r(-11, 10, 23, 13, top)
    r(-13, 12, 4, 11, dark); r(11, 12, 4, 11, dark)
    r(-12, 13, 3, 9, top); r(12, 13, 2, 9, top)
    r(-12, 21, 3, 3, skin); r(12, 21, 2, 3, skin)
    r(-9, 11, 4, 8, highlight(top, 115))
    if L.top_style == 'shirt':
        # Camisa con cuello y corbata, como referencia.
        r(-4, 10, 9, 4, '#f4eeed')
        r(-4, 13, 3, 3, '#f4eeed'); r(2, 13, 3, 3, '#f4eeed')
        r(0, 12, 2, 7, '#a34c57')
        r(-1, 10, 4, 2, '#e9d4d2')
    elif L.top_style == 'hoodie':
        r(-6, 10, 12, 3, shade(top, 85))
        r(-1, 13, 3, 8, shade(top, 80))
        r(-5, 19, 10, 2, shade(top, 85))
        r(3, 13, 1, 4, '#ddd2e5'); r(-3, 13, 1, 4, '#ddd2e5')
    else:
        r(-4, 10, 9, 3, highlight(top, 140))
        r(-3, 11, 7, 2, skin)
        r(-3, 22, 7, 1, shade(top))

    # Cabeza grande, chibi, con contorno negro y tonos de piel.
    r(-11,-5,23,20,dark)
    r(-10,-4,21,18,skin)
    r(-9,-3,7,7,highlight(skin,108))
    r(8,4,3,8,shade(skin,92))
    r(-11,3,2,7,skin);r(11,3,2,7,skin)
    # Las siluetas de presentación cambian ligeramente sin imponer prendas.
    if L.presentation == 'feminine':
        r(-11, 9, 2, 5, hair);r(10, 9, 3, 5, hair)
        r(-7, 9, 3, 1, '#d77e86');r(6, 9, 3, 1, '#d77e86')
    elif L.presentation == 'masculine':
        r(-11, 4, 2, 5, shade(hair)); r(11, 4, 2, 5, shade(hair))

    # Copete y mechones característicos del estilo.
    if L.hair_style == 'long':
        r(-11,-6,23,8,dark);r(-10,-5,21,8,hair)
        r(-11,1,6,12,hair);r(7,1,5,13,hair)
        r(-6,1,6,4,hair);r(3,0,5,4,hair)
        r(6,-4,3,2,highlight(hair,120))
    elif L.hair_style == 'messy':
        r(-10,-5,22,7,hair)
        r(-11,-2,6,7,hair);r(8,-2,4,6,hair)
        r(-7,1,6,4,hair);r(2,0,6,4,hair)
        r(-7,-7,4,2,highlight(hair,128))
        r(3,-6,4,2,highlight(hair,125))
    else:
        r(-11,-6,23,7,hair)
        r(-11,-1,5,8,hair);r(8,-1,4,8,hair)
        r(-7,0,7,4,hair);r(3,-1,7,4,hair)
        r(-7,-6,4,2,highlight(hair,126))
        r(1,-7,4,2,highlight(hair,126))

    # Caras expresivas; el personaje mantiene su reacción musical.
    if not playing or mood == 'calm':
        r(-5,7,4,1,'#382c35');r(3,7,4,1,'#382c35')
    elif mood == 'sad':
        r(-5,7,2,3,'#272126');r(4,7,2,3,'#272126')
        if (tick//3)%2==0:
            r(7,10,1,3,'#79b9ea')
    else:
        r(-5,6,2,4,'#201b20');r(4,6,2,4,'#201b20')
    if playing and mood in ('happy', 'love', 'energy'):
        r(-1,12,4,1,'#9f4c54');r(0,13,2,1,'#9f4c54')
    else:
        r(0,12,2,1,'#744b53')

    # Accesorios como una capa independiente.
    if L.accessory == 'Auriculares':
        r(-13,-5,3,15,dark);r(11,-5,3,15,dark)
        r(-9,-10,19,3,dark);r(-8,-9,17,2,'#656073')
        r(-14,2,5,9,dark);r(-13,3,4,7,glow)
        r(11,2,5,9,dark);r(12,3,3,7,glow)
    elif L.accessory == 'Gorra':
        r(-12,-11,23,6,dark);r(-11,-10,21,5,'#48577c')
        r(-13,-5,19,3,dark);r(-12,-5,18,2,'#7381ad')
    elif L.accessory == 'Moño':
        r(7,-11,8,7,dark);r(8,-10,7,5,'#c9769b');r(10,-10,2,5,'#e6adc0')
