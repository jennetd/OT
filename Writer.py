import Result
import xml.etree.ElementTree as ET

class Writer:

    def dict_to_xml(self, data, parent):
        for key, value in data.items():
            if isinstance(value, dict):
                element = ET.SubElement(parent, str(key))
                self.dict_to_xml(value, element)
            else:
                print(key, value)
                element = ET.SubElement(parent, str(key))
                element.text = str(value)
                
    def writeResultToXML(self, result, outputXMLFile):
        print("Writing result to " + outputXMLFile)

        root = ET.Element("ROOT")
        self.dict_to_xml(result.fResultDict,root)
        tree = ET.ElementTree(root)
        print(ET.tostring(tree.getroot()))
#        ET.indent(tree, space="    ", level=0)

        tree.write(outputXMLFile, encoding="utf-8", xml_declaration=True, method="xml")
        print("XML saved to output.xml")

    def writeResultToHTML(self, result, outputHTMLFile):
        print("Writing result to HTML")
        
    def writeScoreToXML(self, score, outputXMLFile):
        print("Writing score to XML")

    def writeScoreToHTML(self, score, outputHTMLFile):
        print("Writing score to HTML")
        
                

    
