import Result

class Writer:
    
    def writeResultToXML(self, result, outputXMLFile):
        print("Writing result to " + outputXMLFile)

        # install in venv using
        # pip install dict2xml
        from dict2xml import dict2xml

        xml = dict2xml(result.fResultDict, indent ="   ")

        outputFile = open(outputXMLFile, "w")
        outputFile.write(xml)
        outputFile.close()

    def writeResultToHTML(self, result, outputHTMLFile):
        print("Writing result to HTML")
        
    def writeScoreToXML(self, score, outputXMLFile):
        print("Writing score to XML")

    def writeScoreToHTML(self, score, outputHTMLFile):
        print("Writing score to HTML")


    
