# detectorColor


### Habilitar la cámara de la raspberry
__Esta configuración solo se hace cuando se utiliza la raspicam, para una webcam usb no es necesario__
```
sudo raspi-config
```
interfaces -> camera -> enable


### Dependencias
```
sudo apt-get update && sudo apt-get upgrade -y
```
```
sudo apt-get install git libhdf5-dev libhdf5-serial-dev libatlas-base-dev libjasper-dev -y
```


### Librerías
```
python3 -m pip install -U pip numpy
```
```
python3 -m pip install opencv-python rpyc
```


### Config del repositorio local
```
cd ~/Documents
git clone https://github.com/mobiuscat/detectorColor.git
```
