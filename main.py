import threading
from single_cam import iniciarCam

def main():
    threading.Thread(target = iniciarCam).start()

if __name__=='__main__':
    main()