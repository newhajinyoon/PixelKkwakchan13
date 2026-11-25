from fontTools.ttLib import TTFont

f = TTFont('PixelKkwakchan13.ttf')
f.flavor = 'woff2'
f.save('PixelKkwakchan13.woff2')