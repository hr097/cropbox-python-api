import os
import shutil
import json
from flask import Flask, abort, jsonify, request, flash, redirect, Response,send_file,send_from_directory
from pathlib import Path
from PyPDF2 import PdfWriter, PdfReader



app = Flask(__name__)

path = os.path.dirname(os.path.abspath(__file__))
upload_folder=os.path.join(path.replace("/file_folder",""),"tmp")
os.makedirs(upload_folder, exist_ok=True)
app.config['upload_folder'] = upload_folder

        
@app.route('/', methods=['POST','GET'])
def index():
     return Response(json.dumps({'Message':'Not for public use!'}), mimetype='application/json') #something went wrong while cropping and making new PDF



@app.route('/get-pdf',methods = ['POST'])
def get_pdf():

    try:
        req = json.loads(request.data)
        #return Response(json.dumps(r['filename']), mimetype='application/json') #something went wrong while cropping and making new PDF
        return send_from_directory(app.config.get('upload_folder'), req['filename'], as_attachment=True,mimetype='application/pdf')
    except FileNotFoundError:
        abort(404)
   
    

@app.route('/delete',methods = ['POST'])
def delete_file():

            req  = json.loads(request.data)
            filename = req['filename']
            try:
                if os.path.exists(os.path.join(app.config.get('upload_folder'), filename)):
                        os.remove(os.path.join(app.config.get('upload_folder'), filename))
                        return Response(json.dumps({"status": True,"code": 200,"message": "Deleted!"}), mimetype="application/json")
                else:
                    return Response(json.dumps({"status": True,"code": 200,"message": "Not Exists!"}), mimetype="application/json")     
            except FileNotFoundError:
                return Response(json.dumps({"status": True,"code": 200,"message": "Error-code:500"}), mimetype="application/json") #unable to delete file
                # abort(404)
        
@app.route('/upload', methods=['POST'])
def upload():

    try:

        try:

            pdf_file = request.files['filename']
            pdf_name = pdf_file.filename
            save_path = os.path.join(app.config.get('upload_folder'),pdf_name)
            pdf_file.save(save_path)

            with open(save_path, "rb") as in_f:

                input1 = PdfReader(in_f)
                output = PdfWriter()

                numPages = len(input1.pages)
                x, y, w, h = (170, 23,255, 350)

                page_x= input1.pages[0].cropbox.left
                page_y= input1.pages[0].cropbox.top 
                upperLeft = [page_x.as_numeric(), page_y.as_numeric()] 
                new_upperLeft  = (upperLeft[0] + x, upperLeft[1] - y)
                new_lowerRight = (new_upperLeft[0] + w, new_upperLeft[1] - h)

                for i in range(numPages):
                    page = input1.pages[i]
                    page.cropbox.lower_left  = new_upperLeft
                    page.cropbox.lower_right = new_lowerRight
                    output.add_page(page)

                   # print(os.path.join(app.config.get('upload_folder'), pdf_name))

                with open(os.path.join(app.config.get('upload_folder'), "output_"+pdf_name), "wb") as out_f:
                    output.write(out_f)

            if os.path.exists(os.path.join(app.config.get('upload_folder'), pdf_name)):
                        os.remove(os.path.join(app.config.get('upload_folder'), pdf_name))

            return Response(json.dumps({'status': True,'code': 200,'message': 'Processed','filename':"output_"+pdf_name}), mimetype='application/json') # PDF cropped and created
        
        except Exception as e:
            app.logger.info("error occurred")
            return Response(json.dumps({'status': True,'code': 200,'message': 'Error-code:503'}), mimetype='application/json') #something went wrong while cropping and making new PDF
    

    except Exception as e:
        app.logger.info("An error occurred while creating temp folder")
        app.logger.error("Exception occurred : {}".format(e))
        return Response(json.dumps({'status': True,'code': 200,'message': 'Error-code:417'}), mimetype='application/json') # unable to create temp folder


    
     
# main method
if __name__ == "__main__":
    app.run()