#!flask/bin/python3
import sys
from app import app

app.debug = True
app.static_folder = 'static'

def main(argv):
    try:
        if argv[0] == '-s': # on the server
            app.run(host="0.0.0.0",port="80")
    except:
        app.run()


if __name__ == '__main__':
    main(sys.argv[1:])

