from urllib import request
from PIL import ImageFile

import diskcache

def getsizes(uri, dc):
    try:
        # get file size *and* image size (None if not known)
        data = None
        if uri in dc:
            return dc[uri]
        else:
            file = request.urlopen(uri)
            data = file.read(1024)
            file.close()

        if data:
            p = ImageFile.Parser()
            p.feed(data)
            if p.image:
                dc[uri] = p.image.size
                return p.image.size
    except Exception as e:
        print(e)
        print('Cannot detect size')
    return None, None
