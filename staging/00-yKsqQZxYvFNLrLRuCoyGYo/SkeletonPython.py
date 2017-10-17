#########################################
###  SkeletonPython Module for Bisque   ###
#########################################
import os
import time
import sys
import logging
import zipfile
from lxml import etree
import numpy as np
from optparse import OptionParser
from bqapi.comm import BQSession, BQCommError

from bqapi.util import fetch_dataset, fetch_image_pixels, d2xml
from subprocess import call

import pickle

#Constants
PARALLEL                        = True
NUMBER_OF_THREADS               = 4 #number of concurrent requests
IMAGE_SERVICE                   = 'image_service'
FEATURES_SERVICE                = 'features'
FEATURE_NAME                    = 'HTD'
FEATURE_TABLE_DIR               = 'Outputs'
TEMP_DIR                        = 'Temp'

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('bq.modules')


class SkeletonPythonError(Exception):
    
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return self.message        

class SkeletonPython(object):
    """
        SkeletonPython Model
    """

    def mex_parameter_parser(self, mex_xml):
        """
            Parses input of the xml and add it to SkeletonPython Trainer's options attribute
            
            @param: mex_xml
        """
        mex_inputs = mex_xml.xpath('tag[@name="inputs"]')
        if mex_inputs:
            for tag in mex_inputs[0]:
                if tag.tag == 'tag' and tag.attrib['type'] != 'system-input':
                    log.debug('Set options with %s as %s'%(tag.attrib['name'],tag.attrib['value']))
                    setattr(self.options,tag.attrib['name'],tag.attrib['value'])
        else:
            log.debug('SkeletonPythonFS: No Inputs Found on MEX!')

    def validateInput(self):
        """
            Parses input of the xml and add it to SkeletonPython's options attribute
            
            @param: mex_xml
        """        
        if (self.options.mexURL and self.options.token): #run module through engine service
            return True
        
        if (self.options.user and self.options.pwd and self.options.root): #run module locally (note: to test module)
            return True
        
        log.debug('SkeletonPython: Insufficient options or arguments to start this module')
        return False


    def setup(self):
        """
            Fetches the mex, appends input_configurations to the option
            attribute of SkeletonPython and looks up the model on bisque to 
            classify the provided resource.
        """
        if (self.options.user and self.options.pwd and self.options.root):
            self.bqSession = BQSession().init_local( self.options.user, self.options.pwd, bisque_root=self.options.root)
            self.options.mexURL = self.bqSession.mex.uri
        # This is when the module actually runs on the server with a mexURL and an access token
        elif (self.options.mexURL and self.options.token):
            self.bqSession = BQSession().init_mex(self.options.mexURL, self.options.token)
        else:
            return
        
        # Parse the xml and construct the tree, also set options to proper values after parsing it (like image url)
        self.mex_parameter_parser(self.bqSession.mex.xmltree)
        
        log.debug('SkeletonPython: image URL: %s, mexURL: %s, stagingPath: %s, token: %s' % (self.options.image_url, self.options.mexURL, self.options.stagingPath, self.options.token))
    
    
    def run(self):
        """
            The core of the SkeletonPython Module
            
            Requests features on the image provided. Classifies each tile
            and picks a majority among the tiles. 
        """

        r_xml = self.bqSession.fetchxml(self.options.mexURL, view='deep')
        '''rectangles = r_xml.xpath('//tag[@name="inputs"]/tag[@name="image_url"]/gobject[@name="roi"]/rectangle')
    
        rois = []
        rois_rectangles = []
        for i in range(len(rectangles)):
            x1 = int(float(rectangles[i][0].attrib['x']))
            y1 = int(float(rectangles[i][0].attrib['y']))
            x2 = int(float(rectangles[i][1].attrib['x']))
            y2 = int(float(rectangles[i][1].attrib['y']))
            rois_rectangles.append([x1,y1,x2,y2])


        polygons = r_xml.xpath('//tag[@name="inputs"]/tag[@name="image_url"]/gobject[@name="roi"]/polygon')

        rois_polygons = []
        for i in range(len(polygons)):
            polygon = []
            for j in range(len(polygons[i])):
                x = int(float(polygons[i][j].attrib['x']))
                y = int(float(polygons[i][j].attrib['y']))
                polygon.append([x,y])
            rois_polygons.append(polygon)
        
        polylines = r_xml.xpath('//tag[@name="inputs"]/tag[@name="image_url"]/gobject[@name="roi"]/polyline')

        rois_polylines = []
        for i in range(len(polylines)):
            polyline = []
            for j in range(len(polylines[i])):
                x = int(float(polylines[i][j].attrib['x']))
                y = int(float(polylines[i][j].attrib['y']))
                polyline.append([x,y])
            rois_polylines.append(polyline)

        rois.append(rois_polylines)
        rois.append(rois_polygons)
        rois.append(rois_rectangles)'''


    def teardown(self):
        """
            Posting results to the mex
        """

        self.bqSession.update_mex('Returning results...')
        '''log.debug('Returning results...')

        prediction = "None-Module Failure"
        with open("./results.txt","r") as f:
            for line in f:
                if "PREDICTION_C:" in line:
                    prediction_c = line
                if "CONFIDENCE_C:" in line:
                    confidence_c = line[14:-1]
                if "PREDICTION_T:" in line:
                    prediction_t = line
                if "CONFIDENCE_T:" in line:
                    confidence_t = line[14:-1]
                print line

        classes = ["flower","stem","fruit","entire","leaf"]
        classes_type = ["sheet","natural"]
        for i,class_tag in enumerate(classes):
            prediction_c = prediction_c.replace(str(i),class_tag)
        for i,class_tag in enumerate(classes_type):
            prediction_t = prediction_t.replace(str(i),class_tag)
        '''
        outputTag = etree.Element('tag', name='outputs')
        #dda = etree.SubElement(outputTag, 'tag', name='mex_url', value=self.options.image_url)
        outputSubTagImage = etree.SubElement(outputTag, 'tag', name='OutputImage', value=self.options.image_url)
        '''gob = etree.SubElement (outputSubTagImage, 'gobject', name='Annotations', type='Annotations')

        xc = [100, 300, 200]
        yc = [100, 150, 200]
        polyseg = etree.SubElement(gob, 'polygon', name='SEG')
        etree.SubElement( polyseg, 'tag', name='color', value="#0000FF")
        for i in range(len(xc)):
            etree.SubElement (polyseg, 'vertex', x=str(1*int(yc[i])), y=str(1*int(xc[i])))
        print outputTag'''

        '''print "Module will output image, {}".format(self.options.image_url)
    	
            if not os.path.isfile("./contours.pkl"):
                print "Module will not segment image, (were foreground and background polyline annotations provided?)"

            if self.options.segmentImage != "False" and os.path.isfile("./contours.pkl"):

                [contours, t_scale] = pickle.load(open("./contours.pkl","rb"))
                xc = []
                yc = []
                for i, p in enumerate(contours):
                    if i < len(contours)/2:
                        xc.append(p)
                    else:
                        yc.append(p)

                gob = etree.SubElement (outputSubTagImage, 'gobject', name='Annotations', type='Annotations')
                
                polyseg = etree.SubElement(gob, 'polygon', name='SEG')
                etree.SubElement( polyseg, 'tag', name='color', value="#0000FF") 
                print "TSCALE", t_scale
                for i in range(len(xc)):     
                    etree.SubElement (polyseg, 'vertex', x=str(t_scale[1]*int(yc[i])), y=str(t_scale[0]*int(xc[i])))
        
            ###outputSubTagSummary = etree.SubElement(outputTag, 'tag', name='summary')
            #etree.SubElement(outputSubTagSummary, 'tag',name='Model File', value=self.options.deepNetworkChoice)
            #etree.SubElement(outputSubTagSummary, 'tag',name='Segment Image', value=self.options.segmentImage)
            ###etree.SubElement(outputSubTagSummary, 'tag',name='Class', value=str(prediction_c))
            ###etree.SubElement(outputSubTagSummary, 'tag', name='Class Confidence', value=str(confidence_c))
            #etree.SubElement(outputSubTagSummary, 'tag',name='Type', value=str(prediction_t))
            #etree.SubElement(outputSubTagSummary, 'tag', name='Type Confidence', value=str(confidence_t))
            '''
        self.bqSession.finish_mex(tags = [outputTag])
        log.debug('FINISHED')
        self.bqSession.close()


    def main(self):
        """
            The main function that runs everything
        """

        print("DEBUG_INIT")

        log.debug('SkeletonPython is called with the following arguments')
        log.debug('sysargv : %s\n\n' % sys.argv )
    
        
        parser = OptionParser()

        parser.add_option( '--image_url'   , dest="image_url")
        parser.add_option( '--mex_url'     , dest="mexURL")
        parser.add_option( '--module_dir'  , dest="modulePath")
        parser.add_option( '--staging_path', dest="stagingPath")
        parser.add_option( '--bisque_token', dest="token")
        parser.add_option( '--user'        , dest="user")
        parser.add_option( '--pwd'         , dest="pwd")
        parser.add_option( '--root'        , dest="root")

        (options, args) = parser.parse_args()

        # Set up the mexURL and token based on the arguments passed to the script
        try: #pull out the mex
            log.debug("options %s" % options)
            if not options.mexURL:
                options.mexURL = sys.argv[1]
            if not options.token:
                options.token = sys.argv[2]
                
        except IndexError: #no argv were set
            pass
        
        if not options.stagingPath:
            options.stagingPath = ''
        
        # Still don't have an imgurl, but it will be set up in self.setup()
        log.debug('\n\nPARAMS : %s \n\n Options: %s'%(args, options))
        self.options = options
        
        if self.validateInput():
            
            try: #run setup and retrieve mex variables
                self.setup()
            except Exception, e:
                log.exception("Exception during setup")
                self.bqSession.fail_mex(msg = "Exception during setup: %s" %  str(e))
                return
            
            try: #run module operation
                self.run()
            except SkeletonPythonError, e:
                log.exception("Exception during run")
                self.bqSession.fail_mex(msg = "Exception during run: %s" % str(e.message))
                return                

            except Exception, e:
                log.exception("Exception during run")
                self.bqSession.fail_mex(msg = "Exception during run: %s" % str(e))
                return

            try: #post module
                self.teardown()
            except Exception, e:
                log.exception("Exception during teardown %s")
                self.bqSession.fail_mex(msg = "Exception during teardown: %s" %  str(e))
                return

if __name__ == "__main__":
    SkeletonPython().main()
    
    
