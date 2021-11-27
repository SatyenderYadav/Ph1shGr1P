from function.function import *
import re,gc
output = []
urls_in_html = []
html = ''
text = ''
file = {}
macro_streams = {}
updated_stream  = {}
eml_filename = ''
html_attachment = ''

@app.route('/')
def index_route(message=None):
  global output,html,text,urls_in_html,file,macro_streams,updated_stream, eml_filename
  output = []
  urls_in_html = []
  file = {}
  html = ''
  text = ''
  macro_streams = {}
  updated_stream  = {} 
  try:
    message = request.args['message']
  except :
    pass
  return render_template("index.html",msg=message)
def allowed_file(eml_filename):
    return '.' in eml_filename and eml_filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/header',methods=['GET','POST'])
def header():
    message=''
    iserror=0
    try:     
      return render_template("header.html",result=output, mssg=message, iserror=iserror)
    except :
      return redirect('/emlparse')

@app.route('/text',methods=['GET','POST'])
def texts():
    message=''
    iserror=0
    if len(text) == 0:
      return redirect('/emlparse')
    try:      
      return render_template("mail-text.html",text=text, mssg=message, iserror=iserror)
    except Exception as e :

      return redirect('/emlparse')

@app.route('/html-content',methods=['GET','POST'])
def html_content():
    message=''
    iserror=0
    if len(html) == 0:
      return redirect('/emlparse')
    try:      
      return render_template("mail-html.html",html=html, mssg=message, iserror=iserror)
    except Exception as e :

      return redirect('/emlparse')


@app.route('/urls',methods=['GET','POST'])
def urls():
  message=''
  iserror=0
  if request.method == 'POST':
    try:
      formdata = request.form

      filename = formdata['url'].split('">')[0].split('"')[0].replace("http://",'').replace(".",'_').replace('https://','').replace('/','_').replace('&amp;','').replace(',','_') + ".png"
      if (os.path.isfile(f'frontend/static/images/urlpng/{filename}')):

        return render_template('screenshot.html',mssg=message,error=iserror,filenames=filename)
      else:
        screenshot(formdata['url'])
        return render_template('screenshot.html',mssg=message,error=iserror,filenames=filename)
    except :
      return redirect('/emlparse')
  else:
    try:
      return render_template("urls.html",urls=urls_in_html, mssg=message, iserror=iserror)
    except Exception as e :

      return redirect('/emlparse')


@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
  try:
    message=''
    iserror=0
    global eml_filename
    eml_filename =''
    if request.method == 'POST':
        if 'file' not in request.files:
            message = 'No File Part'
            return redirect(url_for('index_route',message=message, **request.args))
        file = request.files['file']
        if file.filename == '':
            message = 'No Selected File'
            return redirect(url_for('index_route',message=message, **request.args))
        if file and allowed_file(file.filename):
            semi_filename = secure_filename(file.filename)
            eml_filename = os.path.join(app.config['UPLOAD_FOLDER'],semi_filename) 
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], semi_filename))
            return redirect(url_for('eml_parse'))
        else:
            message = 'Choose Eml Files'
            return redirect(url_for('index_route',message=message, **request.args))
  except Exception as e:
    message = 'Some Error Occured'
  return redirect(url_for('index_route'))


@app.route('/attach-analysis',methods=['GET','POST'])
def attach_analysis():
    message=''
    iserror=0
    global html_attachment
    html_attachment = ''
    if request.method == 'POST':
      formdata  =  request.form
      if formdata['submit'] == "Deep Analysis Of HTML File":
        html_attachment = formdata['path']
        return redirect('/html-deep-analysis')
    if len(file) == 0:
      return redirect('/emlparse')
    try:      
      return render_template("attach-analysis.html",result=file, mssg=message, iserror=iserror)
    except Exception as e :

      return redirect('/emlparse')


@app.route('/microsoft-deep-analysis',methods=['GET','POST'])
def microsoft_deep_analysis():
  message=''
  iserror=0
  global macro_streams,updated_stream
  macro_streams = {}
  updated_stream = {}
  try:
    macro_streams,updated_stream = micro_deep_analysis(file)
    return render_template("microsoft_deep_analysis.html", macro_streams=macro_streams,updated_stream=updated_stream,mssg=message ,iserror=iserror)

  except Exception as e:
    message='Some error occured'
    iserror=1
    return redirect('/emlparse')

  return render_template("microsoft_deep_analysis.html", mssg=message, iserror=iserror)

@app.route('/html-deep-analysis',methods=['GET','POST'])
def html_deep_analysis():
  message=''
  iserror=0
  html_attachment_url = []
  try:
    file_open = open(html_attachment,'rb')
    content = file_open.read().decode('ISO-8859-1')
    semi_html_attachment_url = (re.findall(r'(https?://\S+)', content))
    for urls_in_html_attach in semi_html_attachment_url:
      if urls_in_html_attach[-1:] == ')':
        html_attachment_url.append(urls_in_html_attach[:-1])
      else:
        html_attachment_url.append(urls_in_html_attach)
    file_open.close()
    del file_open
    del semi_html_attachment_url
    gc.collect()
    return render_template("html_deep_analysis.html", urls=html_attachment_url,mssg=message ,iserror=iserror)

  except Exception as e:
    print(e)
    message='Some error occured'
    iserror=1
    return redirect('/emlparse')

  return redirect('/emlparse')

@app.route('/emlparse', methods=['GET', 'POST'])
def eml_parse():
 
  message=''
  iserror=0
  global output,html,text,urls_in_html,file,macro_streams,updated_stream, eml_filename
  output = []
  urls_in_html = []
  file = {}
  html = ''
  text = ''
  macro_streams = {}
  updated_stream  = {}         
  try:
      output,file = eml_file_parse(eml_filename)
      html = output['html'].replace('\\n', '\n').replace('\\t', '\t').replace('\\r','\r')[2:-1]
      text = output['text'].replace('\\n', '\n').replace('\\t', '\t').replace('\\r','\r')[2:-1]
      urls_in_html = (re.findall(r'(https?://\S+)', html))
      return redirect('/header',code=302)
  except Exception as e:

      message='Some error occured'
      iserror=1

  return render_template("index.html", mssg=message, iserror=iserror) 


@app.route('/display/<filename>')
def display_image(filename):

  return redirect(url_for('static', filename='images/urlpng/' + filename), code=301)

if __name__=='__main__': app.run(debug=True,port=8887)