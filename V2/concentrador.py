import rpyc
import time
from configparser import ConfigParser


CONFIG_FILE ='config.ini'
options_parser = ConfigParser()
options_parser.read(CONFIG_FILE)

ID = options_parser.get('DEFAULT','ID_CONCENTRADOR')

servidor = options_parser.get('DEFAULT','Servidor')

det_1 = det_2 = det_3 = det_4 = None

det_1_port= options_parser.get('DET1','Puerto_detector_1')
det_2_port= options_parser.get('DET2','Puerto_detector_2')
det_3_port= options_parser.get('DET3','Puerto_detector_3')
det_4_port= options_parser.get('DET4','Puerto_detector_4')

def controlarServidor(Servidor, IP, Puerto):
            if not IP is None and not Puerto is None:
                if Servidor is None:
                    # Intento conectarme.
                    try:
                        Servidor = rpyc.connect(IP,Puerto)
                        print("Conectado al servidor ", IP, " en el puerto", Puerto)
                    except:
                        print("Fallo la conexión con el puerto ", Puerto)
                        Servidor = None
                else:
                    # Estoy conectado, intento controlar que sea así.
                    try:
                        Servidor.ping()
                    except:
                        # La conexión falló
                        print("Se corto la conexión con el puerto ", Puerto)
                        Servidor = None
            else:
                Servidor = None
            return Servidor

def controlarCam(conexion=()):
    for idDetector, elemento in enumerate(conexion):
        if not elemento is None:
            try:
                elemento.root.iniciarCam()
                print("Detector {} OK".format(idDetector+1))
            except:
                print("No se puede obtener datos del detector {}".format(idDetector+1))
        else: pass



while True:
    det_1 = controlarServidor(det_1,servidor,det_1_port)
    det_2 = controlarServidor(det_2,servidor,det_2_port)
    det_3 = controlarServidor(det_3,servidor,det_3_port)
    det_4 = controlarServidor(det_4,servidor,det_4_port)

    controlarCam((det_1,det_2,det_3,det_4))


        
        
