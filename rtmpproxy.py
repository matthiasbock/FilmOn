def application(env, start_response):
    path = process(env)
    fh = open(path,'r')
    start_response('200 OK', [('Content-Type','application/octet-stream')])
    return fbuffer(fh,10000)


def fbuffer(f, chunk_size):
    '''Generator to buffer file chunks'''  
    while True:
        chunk = f.read(chunk_size)      
        if not chunk: break
        yield chunk