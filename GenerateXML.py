import os, sys
import argparse

from CollectMaPSAs import *
import Analyzer
#import Writer

import xml.etree.ElementTree as ET
import xml.dom.minidom

def main():

    parser = argparse.ArgumentParser(description='MaPSA XML')
    parser.add_argument('-f','--files',nargs='+',help='list of text files containing names of MaPSAs to process')
    args = parser.parse_args()

    mapsa_labels = []
    mapsas = []

    for f1 in args.files:
        print('Reading MaPSA names from ' + f1)
        with open(f1) as f:
            reader = csv.reader(f,delimiter=' ')
            mapsa_info = [row for row in reader]
            mapsa_labels = [row[1] for row in mapsa_info]
            
    print(mapsa_labels)

    analyzer = Analyzer.Analyzer()

    vendor_names = {"QPT":"QPT","AEM":"AEMtec","HPK":"Hamamatsu"}

    for name in mapsa_labels:

        # Analysis
        analyzer.analyze(name)

        result = analyzer.getResult()
        vendor = name.split('_')[0]

        # make the XML stucture
        root = ET.Element("ROOT")
        parts = ET.SubElement(root, "PARTS")

        # MaPSA block
        MAPSA = ET.SubElement(parts, "PART", mode="auto") #use ElementTree to add mode='auto'
        ET.SubElement(MAPSA, "KIND_OF_PART").text = "MaPSA"
        ET.SubElement(MAPSA, "NAME_LABEL").text = name
        ET.SubElement(MAPSA, "MANUFACTURER").text = vendor_names[vendor]
        ET.SubElement(MAPSA, "LOCATION").text = vendor_names[vendor]
        ET.SubElement(MAPSA, "VERSION").text = "2.0"

        # MaPSA attributes
        predefMapsa1 = ET.SubElement(MAPSA, "PREDEFINED_ATTRIBUTES")
        attr1 = ET.SubElement(predefMapsa1, "ATTRIBUTE")
        ET.SubElement(attr1, "NAME").text = "Has Kapton isolation"
        if int(result.getResultValue([name,"kapton"])) > 0:
            ET.SubElement(attr1, "VALUE").text = "Yes"
        else:
            ET.SubElement(attr1, "VALUE").text = "No"

        attr2 = ET.SubElement(predefMapsa1, "ATTRIBUTE")
        ET.SubElement(attr2, "NAME").text = "Grade"
        ET.SubElement(attr2, "VALUE").text = result.getResultValue([name,'Total_Grade'])
        
        # Rework candidate?
        attr3 = ET.SubElement(predefMapsa1, "ATTRIBUTE")
        ET.SubElement(attr3, "NAME").text = "Status"
        if result.getResultValue([name,'Rework']) == "Yes":
            ET.SubElement(attr3, "VALUE").text = "Needs repair"
        else:
            ET.SubElement(attr3, "VALUE").text = "Good"
    
        child = ET.SubElement(MAPSA, "CHILDREN")

        # Loop over MPAs
        for i in range(1,17):
            child_sub = ET.SubElement(child, "PART", mode="auto")                                                                      
            ET.SubElement(child_sub, "KIND_OF_PART").text = "MPA Chip"                                                              
            ET.SubElement(child_sub, "SERIAL_NUMBER").text = str(result.getResultValue([name,i,'serial_number']))
            child_predef = ET.SubElement(child_sub, "PREDEFINED_ATTRIBUTES")                                                         
            child_predef_attr = ET.SubElement(child_predef, "ATTRIBUTE")                                                            
            ET.SubElement(child_predef_attr, "NAME").text = "Chip Posn on Sensor"                                                
            ET.SubElement(child_predef_attr, "VALUE").text = str(i)
     
        # PS-p sensor
        sensor_sub = ET.SubElement(child, "PART", mode="auto")
        ET.SubElement(sensor_sub, "KIND_OF_PART").text = "PS-p Sensor"
        terms = name.split('_')
        ET.SubElement(sensor_sub, "NAME_LABEL").text = terms[1] + '_' + terms[2][:-1] + '_PSP_MAIN' + terms[2][-1]
        
        xmlstr = ET.tostring(root)
        dom = xml.dom.minidom.parseString(xmlstr)
        xmlfinal = dom.toprettyxml(indent="   ")
#        print(xmlfinal)
    
        #    ET.indent(ET.ElementTree(root),'   ')
        outputXML = "../XML/"+name+".xml"
        ET.ElementTree(root).write(outputXML)

        # XML for test results, for later
        #    print("Creating XML file for MaPSA "+name)
        #    writer = Writer.Writer()
        #    outputXML = "../XML/"+name+".xml"
        #    writer.writeResultToXML (result, outputXML)

if __name__ == "__main__":
    main()
