    
from config.config import *
from email import message_from_file
import os,sys,hashlib
import magic,gc
import function.oledump.oledump as ole
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium import webdriver
path = ""


def file_exists (f):
    return os.path.exists(os.path.join(path, f))

def save_file (fn, cont):
    file = open(os.path.join(path, fn), "wb")
    file.write(cont)
    file.close()

def construct_name (id, fn):
    id = id.split(".")
    id = id[0]+id[1]
    return id+"."+fn

def disqo (s):
    s = s.strip()
    if s.startswith("'") and s.endswith("'"): return s[1:-1]
    if s.startswith('"') and s.endswith('"'): return s[1:-1]
    return s

def disgra (s):
    s = s.strip()
    if s.startswith("<") and s.endswith(">"): return s[1:-1]
    return s

def pullout (m, key):
    Html = ""
    Text = ""
    Files = {}
    Parts = 0
    if not m.is_multipart():
        if m.get_filename(): 
            fn = m.get_filename()
            cfn = construct_name(key, fn)
            Files[fn] = (cfn, None)
            if file_exists(cfn): return Text, Html, Files, 1
            save_file(cfn, m.get_payload(decode=True))
            return Text, Html, Files, 1
        cp = m.get_content_type()
        if cp=="text/plain": Text += str(m.get_payload(decode=True))
        elif cp=="text/html": Html += str(m.get_payload(decode=True))
        else:
            cp = m.get("content-type")
            try: id = disgra(m.get("content-id"))
            except: id = None
            # Find file name:
            o = cp.find("name=")
            if o==-1: return Text, Html, Files, 1
            ox = cp.find(";", o)
            if ox==-1: ox = None
            o += 5; fn = cp[o:ox]
            fn = disqo(fn)
            cfn = construct_name(key, fn)
            Files[fn] = (cfn, id)
            if file_exists(cfn): return Text, Html, Files, 1
            save_file(cfn, m.get_payload(decode=True))
        return Text, Html, Files, 1
    y = 0
    while 1:
        try:
            pl = m.get_payload(y)
        except: break
        t, h, f, p = pullout(pl, key)
        Text += t; Html += h; Files.update(f); Parts += p
        y += 1
    return Text, Html, Files, Parts

def extract (msgfile, key):
    m = message_from_file(msgfile)
    From, To, Subject, Date = caption(m)
    Text, Html, Files, Parts = pullout(m, key)
    Text = Text.strip(); Html = Html.strip()
    msg = {"subject": Subject, "from": From, "to": To, "date": Date,
        "text": Text, "html": Html, "parts": Parts}
    if Files: msg["files"] = Files
    return msg

def caption (origin):
    Date = ""
    if "date" in origin: Date = origin["date"].strip()
    From = ""
    if "from" in origin: From = origin["from"].strip()
    To = ""
    if "to" in origin: To = origin["to"].strip()
    Subject = ""
    if "subject" in origin: Subject = origin["subject"].strip()
    return From, To, Subject, Date

def md5_of_file(path):
        md5_hash = hashlib.md5()
        a_file = open(path, "rb")
        content = a_file.read()
        md5_hash.update(content)
        return md5_hash.hexdigest()

def sha1_of_file(path):
        sha1_hash = hashlib.sha1()
        a_file = open(path, "rb")
        content = a_file.read()
        sha1_hash.update(content)
        return sha1_hash.hexdigest()

def sha256_of_file(path):
        sha256_hash = hashlib.sha256()
        a_file = open(path, "rb")
        content = a_file.read()
        sha256_hash.update(content)
        return sha256_hash.hexdigest()

def eml_file_parse(path=None):
    file = path
    f = open(file, "r")
    output = (extract(f, f.name))
    f.close()
    files = output['files']
    file = {}
    for name, value in files.items():
        file[f'{name}'] = []
        file[f'{name}'].append(value[0])
        
        md5_digest = md5_of_file(file[f'{name}'][0]) 
        sha1_digest = sha1_of_file(file[f'{name}'][0]) 
        sha256_digest = sha256_of_file(file[f'{name}'][0]) 
        file[f'{name}'].append(md5_digest) 
        file[f'{name}'].append(sha1_digest) 
        file[f'{name}'].append(sha256_digest)
        file_type = magic.from_file(file[f'{name}'][0])
        file[f'{name}'].append(file_type)
    gc.collect()
    return(output,file)

def micro_deep_analysis(files):
    macro_stream = {}
    updated_streams = {}
    oledump_out = []
    for name, values in files.items():
        oledump_out = ole.Main(values[0])
        macro_stream[f'{name}'] = []
        updated_streams[f'{name}'] = []
        for line in oledump_out:
            line = line.split(' ')
            update_out_1 = []
            update_out_2 = []
            for final_out in line:
                if final_out == '':
                    pass
                else:
                    update_out_1.append(final_out)
                    update_out_2.append(final_out)
            if 'M' == update_out_2[1] or 'm' == update_out_2[1]:
                macro_stream[f'{name}'].append(update_out_2)
                updated_streams[f'{name}'].append(update_out_1)

            else:
                try:
                    int(update_out_1[1])
                    update_out_1.insert(1,'None')
                    updated_streams[f'{name}'].append(update_out_1)
                except Exception as e:
                    pass

    gc.collect()
    return (macro_stream,updated_streams)


def screenshot(url):
    filename = ''
    try:
        path = "frontend/static/images/urlpng/"
        options = FirefoxOptions()
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
        driver.get(url.split('">')[0].split('"')[0])
        filename = (url.split('">')[0].split('"')[0].replace("http://",'').replace(".",'_').replace('https://','').replace('/','_')).replace('&amp;','').replace(',','_')
        driver.save_screenshot(f'{path}/{filename}.png')
        driver.close()
    except Exception as e:
        filename.append('None')
    del driver
    gc.collect()
    return 1