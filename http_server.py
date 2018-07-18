import socket
import sys
import traceback
import mimetypes
import os


def response_ok(body=b"This is a minimal response", mimetype=b"text/plain"):
    """
    returns a basic HTTP response
    Ex:
        response_ok(
            b"<html><h1>Welcome:</h1></html>",
            b"text/html"
        ) ->
        b'''
        HTTP/1.1 200 OK\r\n
        Content-Type: text/html\r\n
        \r\n
        <html><h1>Welcome:</h1></html>\r\n
        '''
    """

    return b"\r\n".join([
        b"HTTP/1.1 200 OK",
        b"Content-Type: " + mimetype,
        b"",
        body,
    ])


def response_method_not_allowed():
    """Returns a 405 Method Not Allowed response"""

    return b"\r\n".join([
        b"HTTP/1.1 403 Method Not Allowed",
        b"",
        b"You can't do that on this server!",
    ])


def response_not_found(f):
    """Returns a 404 Not Found response"""

    # TODO: Implement response_not_found
    return b"\r\n".join([
        b"HTTP/1.1 404 FileNotFound",
        b"",
        b"404 Error: " + f.encode() + b" could not be located",
    ])


def parse_request(request):
    """
    Given the content of an HTTP request, returns the path of that request.
    This server only handles GET requests, so this method shall raise a
    NotImplementedError if the method of the request is not GET.
    """

    method, path, version = request.split("\r\n")[0].split(" ")

    if method != "GET":
        raise NotImplementedError

    return path


def get_mimetype(arg):
    """
    Identifies the mimetype of resource
    :param arg: resource
    :return: (tuple) mt - mimetype
             (int) mc - mimetype code for conditional logic
    """
    d={'text/html':1,
       'text/plain':2,
       'image/jpeg':3,
       'image/png':4,
       None:0
    }
    mt=mimetypes.guess_type(arg)
    mc=d[mt[0]]

    return mt,mc

def list_contents(dir):
    """
    Lists the contents of a directory as unordered list in byte
    :param dir: path to folder
    :return: (byte) HTML for ul tag that display the contents of a folder
    """
    contents="<!DOCTYPE html><html><body><ul>"
    for i in os.listdir(dir):
        contents += "<li>" + i + "</li>"
    contents += "</body></html>"
    return contents.encode()

def read_contents(file):
    """
    Reads a file as byte
    :param file: path to file
    :return: (byte) Contents of file
    """
    with open(file,'rb') as f:
        b=f.read(1)
        bf = b
        while b!=b"":
            b = f.read(1)
            bf += b
        return bf

def server(log_buffer=sys.stderr):
    address = ('127.0.0.1', 10000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("making a server on {0}:{1}".format(*address), file=log_buffer)
    sock.bind(address)
    sock.listen(1)

    try:
        while True:
            print('waiting for a connection', file=log_buffer)
            conn, addr = sock.accept()  # blocking

            try:
                print('connection - {0}:{1}'.format(*addr), file=log_buffer)

                request = ''
                while True:
                    data = conn.recv(1024)
                    request += data.decode('utf8')

                    if '\r\n\r\n' in request:
                        break

                print("Request received:\n{}\n\n".format(request))

                try:
                    path = parse_request(request)

                    #Mimetype and Mimecode
                    mt,mc=get_mimetype(path)

                    # Path is a directory
                    if mc==0:
                        dir= os.path.dirname(sys.argv[0])
                        if path != '/' :
                            dir += "/" + path

                        #if directory does not exist
                        if not os.path.exists(dir):
                            response=response_not_found(dir)

                        else:
                            content=list_contents(dir)

                            response = response_ok(
                                body=content,
                                mimetype=b"text/html"
                        )
                    # Path is a file
                    else:
                        file = os.path.abspath(os.path.dirname(sys.argv[0]) + path)

                        # if file doesnt exist
                        if not os.path.exists(file):
                            response = response_not_found(file)

                        else:
                            content=read_contents(file)
                            response = response_ok(
                                body=content,
                                mimetype=mt[0].encode()
                            )



                    # response = response_ok(
                    #     body=b"Welcome to my web server",
                    #     mimetype=b"text/plain"
                    # )
                except NotImplementedError:
                    response = response_method_not_allowed()

                conn.sendall(response)
            except:
                traceback.print_exc()
            # finally:
            #     # conn.close()

    except KeyboardInterrupt:
        sock.close()
        return
    except:
        pass
        # traceback.print_exc()


if __name__ == '__main__':
    server()
    sys.exit(0)