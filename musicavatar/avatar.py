"""Avatar pixel art dibujado por código: liviano y sin recursos externos."""
from __future__ import annotations
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QWidget
from .avatar_parts import AvatarLook, draw_character


class AvatarCanvas(QWidget):
    """Pequeño lienzo 64x64 ampliado sin interpolación, para apariencia pixel art."""
    def __init__(self, parent=None, preview: bool = False):
        super().__init__(parent)
        self.mood = 'neutral'
        self.stage = 0
        self.playing = False
        self.look = AvatarLook()
        self.preview = preview
        self.tick = 0
        self.setMinimumSize(172, 172)
        self.setMaximumHeight(355)
        self.setToolTip('Tu avatar vive en su propio escenario pixel art')
        self.timer = QTimer(self)
        self.timer.setInterval(260)
        self.timer.timeout.connect(self.advance_frame)
        if not preview:
            self.timer.start()

    def advance_frame(self):
        self.tick += 1
        self.update()

    def set_state(self, mood: str, stage: int = 0, playing: bool = False):
        if (mood,stage,playing) != (self.mood,self.stage,self.playing):
            self.mood, self.stage, self.playing = mood, stage, playing
            self.update()

    def set_customization(self, hair: str, outfit: str, accessory: str, *,
                          hair_style: str = 'short', top_style: str = 'hoodie',
                          pants: str = '#35313b', shoes: str = 'white',
                          skin: str = '#f4d0aa', presentation: str = 'neutral'):
        # Conserva compatibilidad con las tres opciones de Musicavatar v0.4.
        self.look = AvatarLook(hair=hair, outfit=outfit, accessory=accessory,
                               hair_style=hair_style, top_style=top_style,
                               pants=pants, shoes=shoes, skin=skin,
                               presentation=presentation).validated()
        self.update()

    def paintEvent(self, event):
        img = QPixmap(64, 64)
        img.fill(QColor('#141321'))
        p = QPainter(img)
        p.setPen(Qt.PenStyle.NoPen)
        def rect(x, y, w, h, c):
            p.fillRect(int(x),int(y),int(w),int(h),QColor(c))
        def pixels(coords, color):
            for x,y in coords: rect(x,y,1,1,color)

        moods = {
            'neutral': ('#262237','#373044','#51425d','#817099'),
            'happy': ('#77614c','#ae8157','#ddaa68','#f5dc96'),
            'sad': ('#182b40','#254056','#38546c','#8199ba'),
            'calm': ('#243f41','#3a605d','#507d72','#a3c3b6'),
            'energy': ('#241a3b','#4f285c','#902e69','#ed7c8e'),
            'love': ('#50334d','#824b6c','#b96f8b','#f1b5bf'),
        }
        sky, mid, light, glow = moods.get(self.mood, moods['neutral'])
        # Living room window and quiet landscape; each world has its own colors.
        rect(0,0,64,64,sky)
        rect(0,39,64,25,mid)
        rect(0,44,64,20,'#26202c')
        rect(0,57,64,7,'#1d1c29')
        rect(6,7,52,31,'#0f121d')
        rect(8,9,48,27,mid)
        rect(8,24,48,12,sky)
        rect(31,9,2,27,'#211a27')
        rect(8,21,48,2,'#211a27')
        # Outdoor city silhouette / window scene
        rect(9,30,8,6,'#282b37'); rect(17,27,10,9,'#343442')
        rect(37,29,8,7,'#2d303d'); rect(45,26,10,10,'#313441')
        rect(10,11,4,4,glow)
        if self.mood == 'happy':
            rect(11,12,7,7,'#f9d981'); rect(12,11,5,9,'#f9d981')
            for x,y in [(24,14),(28,18),(43,15),(49,20),(37,13)]: rect(x,y,1,1,'#f8e2aa')
        elif self.mood in ('sad','calm'):
            rect(12,12,5,5,'#d8d9d3')
            rect(15,12,3,3,mid)
        else:
            rect(12,12,5,5,glow)
        if self.mood == 'sad':
            for n in range(18):
                x = 9 + (n*13 + self.tick*2)%46
                y = 10 + (n*7 + self.tick*3)%24
                rect(x,y,1,3,'#789fc1')
        # Shelf, lamps, floor rug.
        rect(1,47,62,2,'#473849')
        rect(4,48,14,2,'#755c63')
        rect(4,50,3,9,'#473844'); rect(16,50,3,9,'#473844')
        rect(45,48,15,2,'#755c63')
        rect(47,50,3,10,'#453546'); rect(57,50,3,10,'#453546')
        rect(17,60,31,2,'#55435f')
        # Pixel plant on the left
        rect(4,37,8,7,'#a7715d')
        rect(5,43,6,2,'#79524b')
        rect(7,27,2,12,'#4b8a71')
        for x,y in [(4,30),(9,29),(3,34),(11,33),(6,26),(9,25)]: rect(x,y,4,3,'#5da082')
        # Couch/chair
        rect(19,39,28,18,'#403348')
        rect(21,40,24,13,'#66516a')
        rect(18,49,6,9,'#372b3f')
        rect(44,49,6,9,'#372b3f')
        rect(22,56,3,4,'#2c2535'); rect(43,56,3,4,'#2c2535')
        if self.mood == 'sad' and self.stage >= 2 and self.playing:
            # Dramatic outdoor scene, without expensive image effects.
            rect(0,0,64,64,'#162332'); rect(0,40,64,24,'#263443')
            for y in (43,47,52,58): rect(0,y,64,1,'#394858')
            rect(43,19,15,28,'#2f3e49'); rect(43,16,15,4,'#4c515a'); rect(46,23,9,13,'#1c2931')
            rect(8,46,8,10,'#5d6b6b'); rect(6,45,12,2,'#74817c'); rect(7,55,10,2,'#394951')
            for bx in (23,30):
                rect(bx,51,3,8,'#61775b'); rect(bx+1,49,1,3,'#8da88a')
            for n in range(35):
                x = (n*17 + self.tick*2)%64
                y = (n*23+self.tick*4)%61
                rect(x,y,1,3,'#7792b3')
        # Un personaje modular: piel, pelo, ropa, pantalones y zapatos por capas.
        bob = (self.tick//2)%2 if self.playing and self.mood in ('happy','energy') else 0
        ax, ay = 31, 27 - bob
        if self.mood == 'sad': ay += 2
        if not self.playing: ay += (self.tick//6)%2
        draw_character(p, ax, ay, self.look, self.mood, self.playing, self.tick, glow)
        # emotive subtle effects
        if self.playing and self.mood == 'happy':
            pixels([(52,12),(53,11),(54,12),(53,13),(8,8)],'#fae5ad')
        elif self.playing and self.mood == 'love':
            rect(50,14,5,3,'#ef9aae'); rect(51,17,3,2,'#ef9aae'); rect(52,19,1,1,'#ef9aae')
        elif self.playing and self.mood == 'energy':
            rect(51,8,3,7,'#f9bc8b'); rect(50,14,3,5,'#f9bc8b')
        p.end()
        target = self.rect().adjusted(3,3,-3,-3)
        outer = QPainter(self)
        outer.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
        if self.preview:
            # Primer plano del personaje, sin cargar otra imagen ni escenas pesadas.
            crop = img.copy(15, 12, 34, 52)
            # Mantiene proporción al ampliar los píxeles.
            scaled_w = min(target.width(), int(target.height()*34/52))
            scaled_h = min(target.height(), int(target.width()*52/34))
            target.setWidth(scaled_w)
            target.setHeight(scaled_h)
            target.moveCenter(self.rect().center())
            outer.drawPixmap(target,crop)
        else:
            side = min(target.width(), target.height())
            target.setWidth(side)
            target.setHeight(side)
            target.moveCenter(self.rect().center())
            outer.drawPixmap(target,img)
        outer.end()
