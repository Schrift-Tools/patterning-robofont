from mojo.subscriber import (Subscriber, registerGlyphEditorSubscriber,
                             unregisterGlyphEditorSubscriber)
from mojo.UI import AskString
from vanilla import Window, Button, EditText, TextBox, CheckBox
import AppKit


class SettingsWindow:

    def __init__(self, patterning_obj):
        self.patterning_obj = patterning_obj
        self.unit = patterning_obj.getUnit()
        self.w = Window((150, 100))
        self.w.setTitle('patterning parameters')
        self.w.bind("close", self.windowClosed)
        self.w.unitLabel = TextBox("auto", "Unit value")
        self.w.unitInput = EditText("auto",
                                    text=self.unit,
                                    callback=self.unitInputCallback)
        self.w.okButton = Button("auto",
                                 "OK",
                                 callback=self.okButtonCallback)
        rules = [
            # Horizontal
            "H:|-margin-[unitInput]-gutter-[unitLabel]-margin-|",
            "H:|-margin-[okButton]-margin-|",
            # Vertical
            "V:|-margin-[unitInput]-gutter-[okButton]-margin-|",
            "V:|-margin-[unitLabel]-gutter-[okButton]-margin-|"
        ]
        metrics = {
            "margin": 10,
            "gutter": 8,
        }
        self.w.addAutoPosSizeRules(rules, metrics)
        self.w.open()

    def okButtonCallback(self, sender):
        self.w.close()

    def unitInputCallback(self, sender):
        value = sender.get()
        if value.isdigit():
            value = int(value)
            self.unit = value
            self.patterning_obj.setUnit(value)
        else:
            sender.set(self.unit)

    def windowClosed(self, sender):
        self.patterning_obj.settingsPan = 0


class Patterning(Subscriber):
    debug = True
    glyphEditorGlyphDidChangeMetricsDelay = 0.01

    def build(self):
        self.glyphEditor = self.getGlyphEditor()
        self.font = self.glyphEditor.getGlyph().font
        self.fontinfo = self.font.info

        self.container = self.glyphEditor.extensionContainer(
            identifier="com.SCHF.Patterning.background",
            location="background",
            clear=True
        )

        self.showButton = Button((-160, 10, 120, 22),
                                 "Show patterning",
                                 callback=self.showButtonCallback)
        self.showButton.getNSButton().setShowsBorderOnlyWhileMouseInside_(True)
        self.showButton.getNSButton().setCornerRadius_(9)
        self.glyphEditor.addGlyphEditorSubview(self.showButton)
        self.settingsButton = Button((-40, 10, 22, 22),
                                     "⚙︎",
                                     callback=self.settingsButtonCallback)
        self.settingsButton.getNSButton().setShowsBorderOnlyWhileMouseInside_(True)
        self.glyphEditor.addGlyphEditorSubview(self.settingsButton)
        self.show = 0
        self.settingsPan = 0
        self.update()

    def openSettings(self):

        return SettingsWindow(patterning_obj=self)

    def loadParams(self):
        self.unit = self.getUnit()
        self.descender = int(self.fontinfo.descender)
        self.upm = int(self.fontinfo.unitsPerEm)
        self.w = self.glyphEditor.getGlyph().width
        self.left = self.glyphEditor.getGlyph().leftMargin
        self.right = self.glyphEditor.getGlyph().rightMargin

    def getUnit(self):
        if 'com.SCHF.PatterningUnit' in self.font.lib.keys():
            unit = int(
                self.font.lib['com.SCHF.PatterningUnit'])
        elif 'com.schriftgestaltung.customParameter.GSFontMaster.unitizerUnit' in self.font.lib.keys():
            unit = int(
                self.font.lib['com.schriftgestaltung.customParameter.GSFontMaster.unitizerUnit'])
        else:
            unit = 20
            self.font.lib['com.SCHF.PatterningUnit'] = unit
        return unit

    def setUnit(self, unit):
        self.font.lib['com.SCHF.PatterningUnit'] = unit
        self.update()

    def drawGrid(self):

        self.container.clearSublayers()

        if self.left < 0:
            start = (round(self.left / self.unit) - 2) * self.unit
        else:
            start = 0
        if self.right < 0:
            end = (round(self.right / self.unit) - 2) * -self.unit
        else:
            end = 0
        for x in range(start, self.w+1+end, self.unit):
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

    def settingsButtonCallback(self, sender):
        if self.settingsPan:
            self.settingsPan.w.close()
            self.settingsPan = 0
        else:
            self.settingsPan = self.openSettings()

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
