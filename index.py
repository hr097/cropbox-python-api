import os
import shutil
import json
from flask import Flask, abort, jsonify, render_template, request, flash, redirect, Response,send_file,send_from_directory
from pathlib import Path
from PyPDF2 import PdfWriter, PdfReader
from flask_cors import cross_origin

try:
    #Configuration of Application
    app = Flask(__name__,template_folder='template')
    path = os.path.dirname(os.path.abspath(__file__))
    upload_folder=os.path.join(path.replace("/file_folder",""),"tmp") #creating sample/temporary directory
    os.makedirs(upload_folder, exist_ok=True)
    app.config['upload_folder'] = upload_folder #configuring it for global use

except Exception as e:
        app.logger.info("An error occurred while creating temp folder")
        app.logger.error("Exception occurred : {}".format(e))
       



#Default Route    
@app.route('/')
def index():                                
    return render_template("index.html")
    #return Response(json.dumps({"status": True,"code": 404,"message": path}), mimetype='application/json')


@app.route('/get-pdf',methods = ['POST'])
def get_pdf():

    req = json.loads(request.data)
    if os.path.exists(os.path.join(app.config.get('upload_folder'), req['filename'])): # if filename exists then return it
            return send_from_directory(app.config.get('upload_folder'), req['filename'], as_attachment=True,mimetype='application/pdf')        
    else:
            return Response(json.dumps({"status": True,"code": 404,"message": "File not found!"}), mimetype='application/json') #If file not exists

   

@app.route('/delete',methods = ['POST'])
def delete_file():

    req  = json.loads(request.data)
    filename = req['filename']

    if os.path.exists(os.path.join(app.config.get('upload_folder'), filename)): #if file exists then delete it
                os.remove(os.path.join(app.config.get('upload_folder'), filename))
                return Response(json.dumps({"status": True,"code": 200,"message": "Deleted!"}), mimetype="application/json")
    else:
            return Response(json.dumps({"status": True,"code": 404,"message": "File not found!"}), mimetype="application/json")     



@app.route('/upload-for-flipkart', methods=['POST'])
def uploadFlipkart():

        try:
            userid = request.form["userid"]

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

                with open(os.path.join(app.config.get('upload_folder'), userid +"_output_"+pdf_name), "wb") as out_f:
                    output.write(out_f)

            if os.path.exists(os.path.join(app.config.get('upload_folder'), pdf_name)):
                        os.remove(os.path.join(app.config.get('upload_folder'), pdf_name))

            return Response(json.dumps({'status': True,'code': 200,'message': 'Processed','filename': userid +"_output_"+pdf_name}), mimetype='application/json') # PDF cropped and created
        
        except Exception as e:
            app.logger.info("error occurred")
            return Response(json.dumps({'status': True,'code': 503,'message': 'Something Went Wring! Please Try Again Later'}), mimetype='application/json') #something went wrong while cropping and making new PDF


@app.route('/upload-for-meesho', methods=['POST'])
@cross_origin()
def uploadMeesho():

        userid = request.form["userid"]

        try:

            pdf_file = request.files['filename']
            pdf_name = pdf_file.filename
            save_path = os.path.join(app.config.get('upload_folder'),pdf_name)
            pdf_file.save(save_path)

            with open(save_path, "rb") as in_f:

                input1 = PdfReader(in_f)
                output = PdfWriter()

                numPages = len(input1.pages)

                x, y, w, h = (5,5,582,590)

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

                with open(os.path.join(app.config.get('upload_folder'), userid +"_output_"+pdf_name), "wb") as out_f:
                    output.write(out_f)

            if os.path.exists(os.path.join(app.config.get('upload_folder'), pdf_name)):
                        os.remove(os.path.join(app.config.get('upload_folder'), pdf_name))

            return Response(json.dumps({'status': True,'code': 200,'message': 'Processed','filename': userid +"_output_"+pdf_name}), mimetype='application/json') # PDF cropped and created
        
        except Exception as e:
            app.logger.info("error occurred")
            return Response(json.dumps({'status': True,'code': 503,'message': 'Something Went Wrong! Please Try Again Later'}), mimetype='application/json') #something went wrong while cropping and making new PDF


# main method
if __name__ == "__main__":
    app.run()