
import epd2in9
import time
import Image
import ImageDraw
import ImageFont

import sys
import logging
import Adafruit_DHT

import dbconnect

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger('monitor')
logging.debug('Starting up')

def main():
    
    epd = epd2in9.EPD()
    epd.init(epd.lut_full_update)

    # For simplicity, the arguments are explicit numerical coordinates
    image = Image.new('1', (epd2in9.EPD_WIDTH, epd2in9.EPD_HEIGHT), 255)  # 255: clear the frame

    db = dbconnect.getConnection()
##
 # there are 2 memory areas embedded in the e-paper display
 # and once the display is refreshed, the memory area will be auto-toggled,
 # i.e. the next action of SetFrameMemory will set the other memory area
 # therefore you have to set the frame memory twice.
 ##     
    epd.clear_frame_memory(0xFF)
    epd.display_frame()
    epd.clear_frame_memory(0xFF)
    epd.display_frame()

    # for partial update
    epd.init(epd.lut_partial_update)
  #  image = Image.open('monocolor.bmp')
##
 # there are 2 memory areas embedded in the e-paper display
 # and once the display is refreshed, the memory area will be auto-toggled,
 # i.e. the next action of SetFrameMemory will set the other memory area
 # therefore you have to set the frame memory twice.
 ##     

 	#Image.new(mode,size,colour)  size is w,h tuple
    time_image = Image.new('1', (96*2, 32*2), 255)  # 255: clear the frame
    
    #Create a drawing object
    draw = ImageDraw.Draw(time_image)
    
    temp_image = Image.new('1', (96, 32), 255)  # 255: clear the frame
    draw_temp = ImageDraw.Draw(temp_image)
    
    hum_image = Image.new('1', (96, 32), 255)  # 255: clear the frame
    draw_hum = ImageDraw.Draw(hum_image)
    
    db_image = Image.new('1', (96, 32), 255)
    draw_db = ImageDraw.Draw(db_image)

    small_font = ImageFont.truetype('/usr/share/fonts/truetype/droid/DroidSans.ttf', 32)
    
    #font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 32) #font file, size
    font = ImageFont.truetype('/usr/share/fonts/truetype/droid/DroidSans.ttf', 64) #font file, size
    
    image_width, image_height = time_image.size
    temp_width, temp_height = temp_image.size
    hum_width,hum_height = hum_image.size
    db_width, db_height = db_image.size

    
    readings = 0
    readingsBeforeSaving = 6 * 5 #we're waiting 10 secs, so 6 per min x 5  = 5 mins
    lastDBWrite = True

    while (True):
    	#TIME
        # draw a rectangle to clear the image
        draw.rectangle((0, 0, image_width, image_height), fill = 255)
        draw.text((0, 0), time.strftime('%H:%M'), font = font, fill = 0)
        epd.set_frame_memory(time_image.rotate(270), 50, 80)
        
        #TEMP
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, 4) #sensor type, gpio pin
        draw_temp.rectangle((0, 0, temp_width, temp_height), fill = 255)
        if humidity is not None and temperature is not None:
        	draw_temp.text((0, 0), '{0:0.1f}*'.format(temperature), font = small_font, fill = 0)
        else:
        	draw_temp.text((0, 0), '??', font = small_font, fill = 0)
        epd.set_frame_memory(temp_image.rotate(270), 10, 10)
        
        #HUMIDITY
        draw_hum.rectangle((0, 0, hum_width, hum_height), fill = 255)
        if humidity is not None and temperature is not None:
        	draw_hum.text((0, 0), '{0:0.1f}%'.format(humidity), font = small_font, fill = 0)
        else:
        	draw_hum.text((0, 0), '??', font = small_font, fill = 0)
        epd.set_frame_memory(hum_image.rotate(270), 10, 200)
        
        if readings >= readingsBeforeSaving:
            if db is not None and db:
                lastDBWrite = dbconnect.saveTempHumid(db,temperature,humidity)
                readings = 0
        
        if db is None or lastDBWrite is False:
            print("No connection, or last write failed - attempting reconnect")
            db = dbconnect.getConnection() #no db connection, so try and get one
        
        if lastDBWrite is False:
            #display error on display
            draw_db.rectangle((0,0,db_width,db_height),fill=255)
            draw_db.text((0,0),'No DB',font=small_font,fill=0)
            epd.set_frame_memory(db_image.rotate(270),10,100)
        else:
            #clear error on display
            draw_db.rectangle((0,0,db_width,db_height),fill=255)
            epd.set_frame_memory(db_image.rotate(270),10,100)

        epd.display_frame()
        time.sleep(10)
        readings = readings + 1

        

if __name__ == '__main__':
    main()
