#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, urllib2
from datetime import datetime, timedelta
from PIL import Image, ImageStat

def canConnect(URL):
    try:
        urllib2.urlopen(URL)
        return True
    except urllib2.URLError as err: 
        # print '接続失敗'
        return False

def howOldFile(fpath):
    return ( datetime.now() - datetime.fromtimestamp( os.stat( fpath ).st_mtime ) )

# 地図画像のurl は                     form /zoom(1~4)/placeID.png
# http://www.jma.go.jp/jp/contents/img/lines/3/31111.png
#
# radar(雨量)の場合、末尾に時刻が入る  radar/        datetime(5分刻み)
# http://www.jma.go.jp/jp/contents/img/radar/3/31111/201707170125.png
#
# web page は、(5n+2)分ぐらいに更新されている様子


class JmaRainRadar:
    def __init__(self):
        self.mapPlaceId = {'NW':'44446','NE':'44546',
                           'SW':'44447','SE':'44547'}
        self.trimRegion = {'NW':'320x640+320+320','NE':'640x640+0+320',
                           'SW':'320x960+320+0'}
        self.urlTemplate='http://www.jma.go.jp/jp/contents/img/radar/4/{0}/{1}.png'
        self.rainFileTemplate = 'rain{0}.png'


    def isFileOld(self):
        fname = self.rainFileTemplate.format(self.mapPlaceId.keys()[0])
        if not os.path.exists(fname):
            return True

        if howOldFile(fname) > timedelta(minutes=5):
            return True
        else:
            return False


    # 画像DL用の datetime_str(as:'201707171345') を生成し、接続することを確認して返す。
    def makeUrlDatetime_str(self):
        now = datetime.now()
        deltaMin = -(now.minute % 5)
        while deltaMin > -50:
            now5n = now + timedelta(minutes=deltaMin)
            now5n_str = now5n.strftime('%Y%m%d%H%M')
            url = self.urlTemplate.format('44446',now5n_str)
            # print deltaMin
            # print url
            if canConnect(url):
                # print 'OK'
                return now5n_str
            else:
                'cannot connect'
            deltaMin -= 5
        print 'Connection Error?'
        raise

    
    def dlImage(self,datetime_str):
        for d in self.mapPlaceId:
            url = self.urlTemplate.format(self.mapPlaceId[d], datetime_str)
            os.system( 'wget -q '+ url )
            if d in self.trimRegion:
                os.system( 'convert -crop ' + self.trimRegion[d] + ' ' +
                           os.path.basename(url) + ' ' + self.rainFileTemplate.format(d) )
                os.remove(os.path.basename(url))
            else:
                os.rename( os.path.basename(url), self.rainFileTemplate.format(d) )


    # DLした透過png画像に少しでも色があれば、Trueを返す。
    def isRainingImage(self):
        for d in self.mapPlaceId:
            im = Image.open(self.rainFileTemplate.format(d))
            st = ImageStat.Stat(im)
            if st.sum[0] > 0:
                return True
        return False


    def isRaining(self):
        if self.isFileOld():
            self.dlImage( self.makeUrlDatetime_str() )
        x = self.isRainingImage()
        return x

def isRaining():
    RainRadar = JmaRainRadar()
    return RainRadar.isRaining()

if __name__ == "__main__":
    x = isRaining()
    if x == True:
        print 'Rain'
    else:
        print 'sunny'
