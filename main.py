import threading
from single_color import iniciarCam

def main():
    threading.Thread(target = iniciarCam).start()
    print('patata')

if __name__=='__main__':
    main()