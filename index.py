import os
import shutil
import json
from flask import Flask, jsonify, request, flash, redirect, Response,send_file,send_from_directory
from pathlib import Path
from PyPDF2 import PdfWriter, PdfReader


app = Flask(__name__)

try:
    path = os.path.dirname(os.path.abspath(__file__))
    upload_folder=os.path.join(path.replace("/file_folder",""),"tmp")
    os.makedirs(upload_folder, exist_ok=True)
    app.config['upload_folder'] = upload_folder
except Exception as e:
    app.logger.info("An error occurred while creating temp folder")
    app.logger.error("Exception occurred : {}".format(e))

@app.route('/')
def index():
    return Response(json.dumps({"status": True,"code": 200,"message": "Its Working!"}), mimetype="application/json")
    
@app.route('/delete')
def delete():
    shutil.rmtree(upload_folder) #delete upload folder
    return Response(json.dumps({"status": True,"code": 200,"message": "Deleted!"}), mimetype="application/json")
    
    

@app.route('/upload', methods=['POST'])
def post():
    try:
        pdf_file = request.files['file']
        pdf_name = pdf_file.filename
        save_path = os.path.join(app.config.get('upload_folder'),pdf_name)
        pdf_file.save(save_path)
        
        print(save_path)

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

            with open(os.path.join(app.config.get('upload_folder'), "output.pdf"), "wb") as out_f:
                output.write(out_f)
        # return Response(json.dumps({'status': True,'code': 200,'message': 'Its Working!'}), mimetype='application/json')
    
        return send_from_directory(app.config["upload_folder"], filename="output.pdf", as_attachment=True)

    except Exception as e:
        app.logger.info("error occurred")

if __name__ == "__main__":
    app.run()