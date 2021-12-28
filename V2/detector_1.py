# Python code for Multiple Color Detection 
import numpy as np 
import cv2
import time
import rpyc
import json
import shutil
import os
from rpyc.utils.server import ThreadedServer
from configparser import ConfigParser


class detectorColor(rpyc.Service):

    def __init__(self):
        CONFIG_FILE ='./V2/config.ini'
        self.parser = ConfigParser()
        self.parser.read(CONFIG_FILE)

        # ** Creo el RAMDISK si está configurada **
    
        # Si existe borro el directorio temporal
        os.system("sudo umount " + self.parser.get('RAMDISK', 'DIRECTORIO_TEMPORAL'))
        if (os.path.isdir(self.parser.get('RAMDISK', 'DIRECTORIO_TEMPORAL'))):
            shutil.rmtree(self.parser.get('RAMDISK', 'DIRECTORIO_TEMPORAL'))

        # Creo el directorio temporal
        os.makedirs(self.parser.get('RAMDISK', 'DIRECTORIO_TEMPORAL'), exist_ok=True)

        if (int(self.parser.get('RAMDISK', 'RAMDISK')) > 0):
            print("Creando RAMDISK de " + self.parser.get('RAMDISK', 'RAMDISK') + "MB. en " + self.parser.get('RAMDISK', 'DIRECTORIO_TEMPORAL'))
            os.system("sudo mount -t tmpfs -o size=" + self.parser.get('RAMDISK', 'RAMDISK') + "m tmpfs " + self.parser.get('RAMDISK', 'DIRECTORIO_TEMPORAL'))

        self.tempdir = self.parser.get('RAMDISK', 'DIRECTORIO_TEMPORAL')

        self.id = self.parser.get('DET1','ID_detector_1')
        self.modoFoto = eval(self.parser.get('DEFAULT','modoFoto'))

        self.valorPelotaMagenta = int(self.parser.get('DET1','Puntaje_magenta_1'))
        self.valorPelotaCyan = int(self.parser.get('DET1','Puntaje_cyan_1'))
        self.valorPelotaVerde = int(self.parser.get('DET1','Puntaje_verde_1'))
        self.valorPelotaBlanca = int(self.parser.get('DET1','Puntaje_blanco_1'))

        self.puntajeMagenta=self.puntajeCyan=self.puntajeVerde=self.puntajeBlanco=0

        self.areaVerde = self.areaAzul = self.areaRoja = self.areaBlanca = 0

        
    def on_connect(self,args=None):
        print("Cliente conectado")

    def exposed_iniciarCam(self,args=None):
        self.puntajeMagenta=self.puntajeCyan=self.puntajeVerde=self.puntajeBlanco=0
        self.areaVerde = self.areaAzul = self.areaRoja = self.areaBlanca = 0
        self.main()

    def exposed_getPuntaje(self):
        return {'id':self.id,
                'puntosMagenta':self.puntajeMagenta,
                'puntosCyan':self.puntajeCyan,
                'puntosBlanco':self.puntajeBlanco,
                'puntosVerde':self.puntajeVerde,
                'timestamp':time.time()}


    def tomarFotos(self):
        self.cam = cv2.VideoCapture(self.parser.get('DET1','Path_cam_1'))
        self.cam.set(39,0) # Auto focus off
        self.cam.set(21,0) # Auto exposition off
        self.cam.set(28,180) # Foco a la pelota
        self.cam.set(12,100) # Saturacion
        self.cam.set(11,100) # Contraste
        self.cam.set(10,50) # Brillo
        self.cam.set(14,40) #Ganancia
        self.cam.set(13,10)
        time.sleep(0.1)

        for x in range(0,3):
            ret,image = self.cam.read()
            cv2.imwrite(self.tempdir + 'Det1_{}.png'.format(x),image)

    def analizarFotos(self):
        img1 = cv2.imread(self.tempdir+'Det1_0.png')
        img2 = cv2.imread(self.tempdir+'Det1_1.png')
        img3 = cv2.imread(self.tempdir+'Det1_2.png')

        img2 = cv2.flip(img2,1) # Horizontal
        img3 = cv2.flip(img3,0) # Vertical

        pre = cv2.add(img1,img2)
        res = cv2.add(pre,img3)

        colDet = cv2.resize(res,(500,500))
        colDet = cv2.rectangle(colDet,(0,0),(500,250),(0,0,0),-1)
        colDet = cv2.rectangle(colDet,(0,450),(500,500),(0,0,0),-1)
        # colDet = cv2.medianBlur(colDet,5)
        hsvFrame = cv2.cvtColor(colDet, cv2.COLOR_BGR2HSV)

        red_lower_1 = np.array(json.loads(self.parser.get('COLORES','red_lower_1')), np.uint8) 
        red_upper_1 = np.array(json.loads(self.parser.get('COLORES','red_upper_1')), np.uint8) 

        red_lower_2 = np.array(json.loads(self.parser.get('COLORES','red_lower_2')), np.uint8) 
        red_upper_2 = np.array(json.loads(self.parser.get('COLORES','red_upper_2')), np.uint8)

        red_mask_1 = cv2.inRange(hsvFrame, red_lower_1, red_upper_1) 
        red_mask_2 = cv2.inRange(hsvFrame, red_lower_2, red_upper_2)

        red_mask = red_mask_1+red_mask_2 

        green_lower = np.array(json.loads(self.parser.get('COLORES','green_lower')), np.uint8) 
        green_upper = np.array(json.loads(self.parser.get('COLORES','green_upper')), np.uint8) 
        green_mask = cv2.inRange(hsvFrame, green_lower, green_upper) 

        blue_lower = np.array(json.loads(self.parser.get('COLORES','blue_lower')), np.uint8) 
        blue_upper = np.array(json.loads(self.parser.get('COLORES','blue_upper')), np.uint8) 
        blue_mask = cv2.inRange(hsvFrame, blue_lower, blue_upper)

        white_lower = np.array(json.loads(self.parser.get('COLORES','white_lower')),np.uint8)
        white_upper = np.array(json.loads(self.parser.get('COLORES','white_upper')),np.uint8)
        white_mask = cv2.inRange(hsvFrame, white_lower, white_upper)

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
            if(area > 300):
                if self.puntajeMagenta == 0:
                    self.puntajeMagenta = self.valorPelotaMagenta
                x, y, w, h = cv2.boundingRect(contour) 
                colDet = cv2.rectangle(colDet, (x, y), 
                                        (x + w, y + h), 
                                        (0, 0, 255), 2) 
                
                cv2.putText(colDet, "PELOTA ROJA", (x, y), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, 
                            (0, 0, 255))


        # Creating contour to track white color 
        contours, hierarchy = cv2.findContours(white_mask, 
                                            cv2.RETR_TREE, 
                                            cv2.CHAIN_APPROX_SIMPLE) 
        
        for pic, contour in enumerate(contours): 
            area = cv2.contourArea(contour) 
            if(area > 300):
                if self.puntajeBlanco == 0:
                    self.puntajeBlanco = self.valorPelotaBlanca
                x, y, w, h = cv2.boundingRect(contour) 
                colDet = cv2.rectangle(colDet, (x, y), 
                                        (x + w, y + h), 
                                        (0, 0, 0), 2) 
                
                cv2.putText(colDet, "PELOTA BLANCA", (x, y), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, 
                            (0, 255, 0))     

        # Creating contour to track green colo3r 
        contours, hierarchy = cv2.findContours(green_mask, 
                                            cv2.RETR_TREE, 
                                            cv2.CHAIN_APPROX_SIMPLE) 
        
        for pic, contour in enumerate(contours): 
            area = cv2.contourArea(contour) 
            if(area > 300):
                self.areaVerde+=area
                print(self.areaVerde)
                if self.puntajeVerde == 0:
                    self.puntajeVerde = self.valorPelotaVerde
                x, y, w, h = cv2.boundingRect(contour) 
                colDet = cv2.rectangle(colDet, (x, y), 
                                        (x + w, y + h), 
                                        (0, 255, 0), 2) 
                
                cv2.putText(colDet, "PELOTA VERDE", (x, y), 
                            cv2.FONT_HERSHEY_SIMPLEX, 
                            1.0, (0, 255, 0)) 

        # Creating contour to track blue color 
        contours, hierarchy = cv2.findContours(blue_mask, 
                                            cv2.RETR_TREE, 
                                            cv2.CHAIN_APPROX_SIMPLE) 
        for pic, contour in enumerate(contours): 
            area = cv2.contourArea(contour)
            if(area > 300):
                if self.puntajeCyan == 0:
                    self.puntajeCyan = self.valorPelotaCyan
                x, y, w, h = cv2.boundingRect(contour)
                colDet = cv2.rectangle(colDet, (x, y),
                                        (x + w, y + h),
                                        (255, 0, 0), 2)

                cv2.putText(colDet, "PELOTA AZUL", (x, y),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1.0, (255, 0, 0))


        # cv2.imshow('Imagen1',img1)
        # cv2.imshow('Imagen2',img2)
        # cv2.imshow('Imagen3',img3)
        # cv2.imshow('Merge',res)
        # cv2.imshow('Color det',colDet)

        # Program Termination
        print(self.exposed_getPuntaje())
        # cv2.waitKey(0)

        if self.modoFoto:
            # cv2.imwrite('pepe.png',colDet)
            self.cam.release()
            # cv2.destroyAllWindows()


    def main(self):
        self.tomarFotos()
        self.analizarFotos()


if __name__ == '__main__':
    servicio = detectorColor()
    server = ThreadedServer(servicio,port = 5005)
    server.start()
