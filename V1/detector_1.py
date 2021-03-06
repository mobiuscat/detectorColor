# Python code for Multiple Color Detection 
import numpy as np 
import cv2
import time
import rpyc
import json
from rpyc.utils.server import ThreadedServer
from configparser import ConfigParser


class detectorColor(rpyc.Service):

    def __init__(self):
        CONFIG_FILE ='config.ini'
        self.parser = ConfigParser()
        self.parser.read(CONFIG_FILE)

        self.id = self.parser.get('DET1','ID_detector_1')
        self.modoFoto = eval(self.parser.get('DEFAULT','modoFoto'))

        self.valorPelotaMagenta = int(self.parser.get('DET1','Puntaje_magenta_1'))
        self.valorPelotaCyan = int(self.parser.get('DET1','Puntaje_cyan_1'))
        self.valorPelotaVerde = int(self.parser.get('DET1','Puntaje_verde_1'))
        self.valorPelotaBlanca = int(self.parser.get('DET1','Puntaje_blanco_1'))

        self.puntajeMagenta=self.puntajeCyan=self.puntajeVerde=self.puntajeBlanco=0

        
    def on_connect(self,args=None):
        print("Cliente conectado")

    def exposed_iniciarCam(self,args=None):
        self.puntajeMagenta=self.puntajeCyan=self.puntajeVerde=self.puntajeBlanco=0
        self.main()

    def exposed_getPuntaje(self):
        return {'id':self.id,
                'puntosMagenta':self.puntajeMagenta,
                'puntosCyan':self.puntajeCyan,
                'puntosBlanco':self.puntajeBlanco,
                'puntosVerde':self.puntajeVerde,
                'timestamp':time.time()}

    def main(self):
        self.cam = cv2.VideoCapture(self.parser.get('DET1','Path_cam_1'))
        self.cam.set(39,0) # Auto focus off
        self.cam.set(21,0) # Auto exposition off
        self.cam.set(28,80) # Foco a la pelota
        self.cam.set(12,255) # Saturacion
        self.cam.set(11,255) # Contraste
        self.cam.set(10,40) # Brillo
        self.cam.set(14,50) #Ganancia
        self.cam.set(13,255)
        time.sleep(0.1)
        while True:
            _, imageFrame = self.cam.read() 

            imageFrame = cv2.resize(imageFrame,(500,500))
            imageFrame = cv2.rectangle(imageFrame,(0,0),(500,250),(0,0,0),-1)
            imageFrame = cv2.rectangle(imageFrame,(0,450),(500,500),(0,0,0),-1)
            imageFrame = cv2.medianBlur(imageFrame,5)
            hsvFrame = cv2.cvtColor(imageFrame, cv2.COLOR_BGR2HSV) 

            red_lower = np.array(json.loads(self.parser.get('COLORES','red_lower')), np.uint8) 
            red_upper = np.array(json.loads(self.parser.get('COLORES','red_upper')), np.uint8) 
            red_mask = cv2.inRange(hsvFrame, red_lower, red_upper) 

            green_lower = np.array(json.loads(self.parser.get('COLORES','green_lower')), np.uint8) 
            green_upper = np.array(json.loads(self.parser.get('COLORES','green_upper')), np.uint8) 
            green_mask = cv2.inRange(hsvFrame, green_lower, green_upper) 

            blue_lower = np.array(json.loads(self.parser.get('COLORES','blue_lower')), np.uint8) 
            blue_upper = np.array(json.loads(self.parser.get('COLORES','blue_upper')), np.uint8) 
            blue_mask = cv2.inRange(hsvFrame, blue_lower, blue_upper)

            white_lower = np.array(json.loads(self.parser.get('COLORES','white_lower')),np.uint8)
            white_upper = np.array(json.loads(self.parser.get('COLORES','white_upper')),np.uint8)
            white_mask = cv2.inRange(hsvFrame, white_lower, white_upper,0)

            kernal = np.ones((5, 5), "uint8") 
            
            # For red color 
            red_mask = cv2.dilate(red_mask, kernal) 
            
            # For white color
            white_mask = cv2.dilate(white_mask, kernal) 

            # For green color 
            green_mask = cv2.dilate(green_mask, kernal) 
            
            # For blue color 
            blue_mask = cv2.dilate(blue_mask, kernal) 

            # Creating contour to track red color 
            contours, hierarchy = cv2.findContours(red_mask, 
                                                cv2.RETR_TREE, 
                                                cv2.CHAIN_APPROX_SIMPLE) 
            
            for pic, contour in enumerate(contours): 
                area = cv2.contourArea(contour)
                print(area)
                if(area > 7000):
                    if self.puntajeMagenta == 0:
                        self.puntajeMagenta = self.valorPelotaMagenta
                    x, y, w, h = cv2.boundingRect(contour) 
                    imageFrame = cv2.rectangle(imageFrame, (x, y), 
                                            (x + w, y + h), 
                                            (0, 0, 255), 2) 
                    
                    cv2.putText(imageFrame, "PELOTA ROJA", (x, y), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1.0, 
                                (0, 0, 255))


            # Creating contour to track white color 
            contours, hierarchy = cv2.findContours(white_mask, 
                                                cv2.RETR_TREE, 
                                                cv2.CHAIN_APPROX_SIMPLE) 
            
            for pic, contour in enumerate(contours): 
                area = cv2.contourArea(contour)
                if(area > 7000):
                    # print (area)
                    if self.puntajeBlanco == 0:
                        self.puntajeBlanco = self.valorPelotaBlanca
                    x, y, w, h = cv2.boundingRect(contour) 
                    imageFrame = cv2.rectangle(imageFrame, (x, y), 
                                            (x + w, y + h), 
                                            (0, 0, 0), 2) 
                    
                    cv2.putText(imageFrame, "FONDO", (x, y), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1.0, 
                                (0, 0, 0))     

            # Creating contour to track green colo3r 
            contours, hierarchy = cv2.findContours(green_mask, 
                                                cv2.RETR_TREE, 
                                                cv2.CHAIN_APPROX_SIMPLE) 
            
            for pic, contour in enumerate(contours): 
                area = cv2.contourArea(contour) 
                if(area > 7000):
                    if self.puntajeVerde == 0:
                        self.puntajeVerde = self.valorPelotaVerde
                    x, y, w, h = cv2.boundingRect(contour) 
                    imageFrame = cv2.rectangle(imageFrame, (x, y), 
                                            (x + w, y + h), 
                                            (0, 255, 0), 2) 
                    
                    cv2.putText(imageFrame, "PELOTA VERDE", (x, y), 
                                cv2.FONT_HERSHEY_SIMPLEX, 
                                1.0, (0, 255, 0)) 

            # Creating contour to track blue color 
            contours, hierarchy = cv2.findContours(blue_mask, 
                                                cv2.RETR_TREE, 
                                                cv2.CHAIN_APPROX_SIMPLE) 
            for pic, contour in enumerate(contours): 
                area = cv2.contourArea(contour)
                if(area > 7000):
                    if self.puntajeCyan == 0:
                        self.puntajeCyan = self.valorPelotaCyan
                    x, y, w, h = cv2.boundingRect(contour)
                    imageFrame = cv2.rectangle(imageFrame, (x, y),
                                            (x + w, y + h),
                                            (255, 0, 0), 2)

                    cv2.putText(imageFrame, "PELOTA AZUL", (x, y),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1.0, (255, 0, 0))


            # Program Termination
            # print(self.exposed_getPuntaje())

            if self.modoFoto:
                #cv2.imwrite('pepe.png',imageFrame)
                #self.cam.release()
                cv2.destroyAllWindows()
                break

            else:
                cv2.imshow("Multiple Color Detection in Real-TIme", imageFrame)
                k = cv2.waitKey(1)
                if k%256 == 27:
                    # ESC pressed
                    print("Escape hit, closing...")
                    self.cam.release()
                    cv2.destroyAllWindows()
                    break


if __name__ == '__main__':
    servicio = detectorColor()
    server = ThreadedServer(servicio,port = 5005)
    server.start()
