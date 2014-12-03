#!/bin/env python2
# *-* coding: utf-8 *-*

import pygame
import spyral
import os

SIZE = (700,700)
TILE = (64,64)
font_path = "fonts/SourceCodePro-Regular.ttf"

topic_dir = "../english-for-life/Topics/Topic_1/"

def obtener_palabra():
    palabra = "happy"
    palabra_png = os.path.join(topic_dir, "Imagenes", palabra+'.png')

    return palabra, palabra_png

class Escena(spyral.Scene):
    def __init__(self):
        super(Escena, self).__init__(SIZE, 20, 20)

        self.layers = ["abajo", "arriba", "primer"]

        img = spyral.Image(filename="images/Peru_Machu_Picchu_Sunrise.jpg").scale(self.scene.size)

        n = pygame.Surface.convert_alpha(img._surf)
        # red at 50%
        n.fill((255,0,0,127))
        img._surf.blit(n, (0,0))

        self.background = img

        self.j = Jugador(self)
        self.v = Visualizador(self)

        self.l = Lluvia(self)

        self.tablero = Tablero(self)
        self.terraza = Terraza(self)

        spyral.event.register("system.quit", spyral.director.pop)
        spyral.event.register("director.scene.enter", self.entrar)
        spyral.event.register("director.scene.enter", self.l.llover)

        #spyral.event.register("director.update", self.chequea)

    def entrar(self):
        self.j.set_caminar(self.scene.width/2-64)

class Terraza(spyral.Sprite):
    def __init__(self, scene):
        super(Terraza, self).__init__(scene)

        self.anchor = "midbottom"
        self.layer = "abajo"
        self.image = spyral.Image(filename="images/terraza.png")
        self.pos = (scene.width/2, scene.height)

class Tablero(spyral.Sprite):
    def __init__(self, scene):
        super(Tablero, self).__init__(scene)

        self.completo = False
        self.acertadas = ""

        font_path = "fonts/SourceCodePro-Regular.ttf"
        self.font = spyral.Font(font_path, 60, (0,0,0))
        self.palabra, archivo_img = obtener_palabra() 
        self.text = self.palabra
        self.image = self.font.render("")

        self.anchor = 'midbottom'

        self.x = self.scene.width/2 
        self.y = self.scene.height - 128

        self.mostrar(self.text, "")

        spyral.event.register("input.keyboard.down.*", self.procesar_tecla)

    def set_text(self, text):
        self.image = self.font.render(text)
        self.text = text

    def mostrar(self, frase, acertadas):
        total = 0
        estado = ""
        for letra in frase:
            if letra in acertadas:
                estado = estado + " " + letra
                total = total + 1
            else:
                estado = estado + " _"

        if total==len(frase):
            self.completo = True

        self.set_text(estado)

    def procesar_tecla(self, key):
        if not 0<key<255:
            return

        respuesta = chr(key)

        if respuesta not in self.acertadas:
            self.acertadas = self.acertadas + respuesta

        self.mostrar(self.palabra, self.acertadas)


class Lluvia(spyral.Sprite):
    def __init__(self, scene):
        spyral.Sprite.__init__(self, scene)
        self.image = spyral.Image(size=(205,205)).fill((0,0,0))
        self.font = spyral.Font(font_path, 28, (255,255,255))
        self.x = scene.width/2-100

        self.layer = "primer"

        # Asteroide
        self.asteroid_frames = []
        for i in xrange(0,60):
            number = str(i).zfill(2)
            name = "Asteroid-A-10-" + number + ".png"
            self.asteroid_frames.append(spyral.Image(filename = "images/asteroid/" + name).scale((205,205)))

        m = spyral.Animation("image", spyral.easing.Iterate(self.asteroid_frames, 1), 5, loop=True)
        self.animate(m)

        # Boom
        self.explosion_full = spyral.Image(filename = "images/explosion.png")

        self.explosion_frames = []
        explosion_size = 205

        self.explosion_frames.append(self.explosion_full.copy()\
                            .crop( (13*explosion_size, 0), (explosion_size,explosion_size)))
        for i in range(0,13):
            self.explosion_frames.append(self.explosion_full.copy()\
                            .crop( (i*explosion_size, 0), (explosion_size,explosion_size)))

        spyral.event.register("Lluvia.y.animation.end", self.explotar)

    def llover(self):
        p = spyral.Animation("y", spyral.easing.CubicIn(-190, self.scene.height-150), 
                            duration=20)
        self.animate(p)

    def explotar(self):
        self.stop_all_animations()
        n = spyral.Animation("image", spyral.easing.Iterate(self.explosion_frames, 1), 2)
        self.animate(n)

class Visualizador(spyral.Sprite):
    def __init__(self, scene):
        spyral.Sprite.__init__(self, scene)
        self.image = spyral.Image("images/golden-border.png")
        self.layer = "fondo"

        self.font = spyral.Font(font_path, 28, (255,255,255))
        self.line_height = self.font.linesize
        self.margen = 50

        self.text, self.palabra_png = obtener_palabra() 

        self.image.draw_image(self.render_image(self.palabra_png),
                                position=(25, 0),
                                anchor="midleft")
        #self.image.draw_image(self.render_text(self_text),
        #                        position=(0, 0),
        #                        anchor="midleft")

    def render_image(self, image):
        nueva = spyral.Image(filename=image).scale((self.width-self.margen, self.height-self.margen))
        return nueva

    def render_text(self, text):
        text_width = self.font.get_size(text)[0]

        ancho_promedio = self.font.get_size("X")[0]
        caracteres = (self.width - 2 * self.margen) / ancho_promedio
        lineas = self.wrap(text, caracteres).splitlines()

        altura = len(lineas) * self.line_height
        bloque = spyral.Image(size=(self.width, altura))

        ln = 0
        for linea in lineas:
            bloque.draw_image(image=self.font.render(linea),
                                position=(0, ln * self.line_height),
                                anchor="midtop")
            ln = ln + 1
        return bloque


    def wrap(self, text, length):
        """ Sirve para cortar texto en varias lineas """
        words = text.split()
        lines = []
        line = ''
        for w in words:
            if len(w) + len(line) > length:
                lines.append(line)
                line = ''
            line = line + w + ' '
            if w is words[-1]: lines.append(line)
        return '\n'.join(lines)


class Jugador(spyral.Sprite):
    def __init__(self, scene):
        super(Jugador, self).__init__(scene)
        self.full_image = spyral.Image(filename = "images/user2.png")
        self.estado = "nuevo"
        self.y = scene.height - 138
        self.velocidad = 90

        self.layer = "arriba"

        self.north = self.full_image.copy().crop( (0, 8*64), TILE)

        self.east = []
        for i in range(0,8):
            self.east.append(self.full_image.copy()\
                            .crop( (i*64, 11*64), TILE))

        self.west = []
        for i in range(0,8):
            self.west.append(self.full_image.copy()\
                            .crop( (i*64, 9*64), TILE))

        self.quieto = self.north #self.east[0]

        # saltar
        #spyral.event.register("input.keyboard.down.up", self.set_saltar)
        #spyral.event.register("Jugador.y.animation.end", self.set_quieto)

        # trasladar
        spyral.event.register("input.keyboard.up.right", self.frenar)
        spyral.event.register("input.keyboard.up.left", self.frenar)
        spyral.event.register("input.keyboard.down.right", self.derecha)
        spyral.event.register("input.keyboard.down.left", self.izquierda)

        self.set_quieto()
        #self.set_caminar(200)
        self.scale = 2

    def frenar(self):
        if self.estado in ['saltando']:
            return 1

        self.stop_all_animations()
        self.set_quieto()

    def derecha(self):
        self.set_caminar(self.scene.width-96)
        #self.quieto = self.east[0]

    def izquierda(self):
        self.set_caminar(-32)
        #self.quieto = self.west[0]

    def set_quieto(self):
        self.estado = "quieto"
        self.image = self.quieto

    def set_saltar(self):
        if self.estado=="saltando":
            return 1

        altura = 90

        a = spyral.Animation( "y", spyral.easing.QuadraticOut(self.y, self.y - altura), 0.3)
        b = spyral.Animation( "y", spyral.easing.QuadraticIn(self.y - altura, self.y), 0.3)
        c=a+b
        c.property="salto"
        self.animate(c)

        self.estado = "saltando"

    def set_caminar(self, x):
        if self.estado in ["caminando", "saltando"]:
            return 1

        # Calculamos el tiempo para obtener una velocidad constante
        distancia = self.pos.distance((x, self.y))
        tiempo = distancia / self.velocidad

        if self.x < x:
            direccion = self.east
        else:
            direccion = self.west
        a = spyral.Animation( "image", spyral.easing.Iterate(direccion, tiempo), tiempo)
        b = spyral.Animation( "x", spyral.easing.Linear(self.x, x), tiempo)
        d = spyral.Animation( "image", spyral.easing.Iterate([self.quieto], 0.1), 0.1)
        c = a & b
        c = c + d
        c.property="traslado"
        self.animate(c)
        self.estado = "caminando"

if __name__=="__main__":
    spyral.director.init(SIZE, fullscreen = False)
    spyral.director.run(scene=Escena())
