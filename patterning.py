from mojo.subscriber import (Subscriber, registerGlyphEditorSubscriber,
                             unregisterGlyphEditorSubscriber)
from mojo.UI import AskString
from vanilla import Button

class Patterning(Subscriber):
    debug = True
    glyphEditorGlyphDidChangeMetricsDelay = 0.01

    def build(self):
        self.glyphEditor = self.getGlyphEditor()
        self.container = self.glyphEditor.extensionContainer(
            identifier="com.SCHF.Patterning.background",
            location="background",
            clear=True
        )
        self.showButton = Button((-130, 10, 120, 22),
                               "Show patterning",
                               callback=self.showButtonCallback)
        self.showButton.getNSButton().setShowsBorderOnlyWhileMouseInside_(True)
        self.glyphEditor.addGlyphEditorSubview(self.showButton)
        self.show = 0
        self.update()

    def loadParams(self):

        self.font = self.glyphEditor.getGlyph().font
        self.fontinfo = self.font.info
        self.unit = self.loadUnit()
        self.descender = int(self.fontinfo.descender)
        self.upm = int(self.fontinfo.unitsPerEm)
        self.w = self.glyphEditor.getGlyph().width
        self.left = self.glyphEditor.getGlyph().leftMargin
        self.right = self.glyphEditor.getGlyph().rightMargin

    def loadUnit(self):
        if 'com.schriftgestaltung.customParameter.GSFontMaster.unitizerUnit' in self.font.lib.keys():
            unit = int(self.font.lib['com.schriftgestaltung.customParameter.GSFontMaster.unitizerUnit'])
        else:
            unit = None
            self.show = self.show ^ 1
            self.update()
        return unit

    def drawGrid(self):
        
        self.container.clearSublayers()

        if self.left < 0:
            start = (round(self.left / self.unit) - 2) * self.unit
        else: start = 0
        if self.right < 0:
            end = (round(self.right / self.unit) - 2) * -self.unit
        else: end = 0
        for x in range(start, self.w+1+end, self.unit):
        # range(self.descender-self.unit, self.upm-self.descender+self.unit, self.unit):
            self.container.appendLineSublayer(
                startPoint=(x, self.descender),
                endPoint=(x, self.upm+self.descender),
                strokeColor=(0, 0, 0, .25),
                strokeWidth=.8
            )
            if x < self.w + end:
                self.container.appendLineSublayer(
                    startPoint=(x+self.unit/2, self.descender),
                    endPoint=(x+self.unit/2, self.upm+self.descender),
                    strokeColor=(0, 0, 0, .1),
                    strokeWidth=.5
                )
    def drawInfo(self):
        if (self.w / self.unit) % 1:
            width = "|||" + str(round(self.w / self.unit, 3))
            color = (1, 0, 0, 1)
        else:
            width = "|||" + str(int(self.w / self.unit))
            color = (0, 0, 0, .5)
        
        if (self.left / self.unit) % 1:
            left = str(round(self.left / self.unit, 3))
        else:
            left = str(self.left // self.unit)
        
        if (self.right / self.unit) % 1:
            right = str(round(self.right / self.unit, 3))
        else:
            right = str(self.right // self.unit)
        
        self.container.appendTextLineSublayer(
            position=(self.w+3, self.upm+self.descender+20),
            pointSize=12,
            fillColor=color,
            text=width
        )
        
        self.container.appendTextLineSublayer(
            position=(-6, -40),
            pointSize=12,
            fillColor=(0, 0, 0, .5),
            horizontalAlignment="right",
            text=left
        )
        
        self.container.appendTextLineSublayer(
            position=(self.w+6, -40),
            pointSize=12,
            fillColor=(0, 0, 0, .5),
            text=right
        )

    def update(self):
        if self.show:
            self.loadParams()
            self.drawGrid()
            self.drawInfo()
        else:
            self.destroy()


    def showButtonCallback(self, sender):
        self.show = self.show ^ 1
        self.update()

    def glyphEditorDidScale(self, info):
        self.update()

    def glyphEditorGlyphDidChangeMetrics(self, info):
        self.update()

    def glyphEditorDidSetGlyph(self, info):
        self.update()

    def destroy(self):
        self.container.clearSublayers()

if __name__ == '__main__':
    registerGlyphEditorSubscriber(Patterning)
