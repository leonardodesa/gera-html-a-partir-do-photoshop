from psd_tools import PSDImage
import os
import json
import io
import dominate
from dominate.tags import *
import re
import shutil
from unidecode import unidecode

def start():
    content = {"psdPathInfoUser": 'C:\ESTUDO\Python', "pathFormatsPsdsFound": [], "createdFoldersName": [], "formats": [], "imagesExported": ''
               # "formats": [{
               #     "frames": [{
               #         "images": [{
               #             "position": [{

               #             }]
               #         }]
               #     }]
               # }
               }

    # arrayPsdsOpen = []

    # content["psdPathInfoUser"] = askAndReturnStringPathPsd()

    content["pathFormatsPsdsFound"] = returnArrayPathPsdsInTheFolder(content["psdPathInfoUser"])

    arrayNamesWithoutExtensionPsd = removeExtensionPsd(content["pathFormatsPsdsFound"])

    content["createdFoldersName"] = getArrayFormatFilePath(arrayNamesWithoutExtensionPsd)

    createPaste(arrayNamesWithoutExtensionPsd)

    arrayPsds = returnArrayOpenPsd(content["pathFormatsPsdsFound"])

    content["imagesExported"] = exportImagesFromPsd(arrayPsds, arrayNamesWithoutExtensionPsd, content)

    content["formatsInfo"] = returnArrayInfoFormats(arrayPsds, arrayNamesWithoutExtensionPsd, content)

    createJson('data.json', content)

    generateHtml(content)

    generateCss(content)

def generateHtml(content):
    for contFormatSize in range(0, len(content["formatsInfo"])):
            formatsSize = content["formatsInfo"][contFormatSize][0]

            doc = dominate.document(title=formatsSize)
            with doc.head:
                link(rel='stylesheet', href='style.css')

            with doc:
                container = div(id="container")
                for groups in range(len(content["formatsInfo"][contFormatSize][1]) -1, -1, -1):
                    idGroup = content["formatsInfo"][contFormatSize][1][groups][0]
                    if idGroup == 'static':
                        group = div(id=idGroup)
                    else:
                        group = div(id=idGroup, style="opacity:0")
                    arrayImagesAndPosition = content["formatsInfo"][contFormatSize][1][groups][1]
                    for arrayImages in range(0, len(arrayImagesAndPosition)):
                        images = arrayImagesAndPosition[arrayImages][0]
                        idImages = os.path.splitext(images)[0]
                        positionImagesX = arrayImagesAndPosition[arrayImages][1][0]
                        positionImagesY = arrayImagesAndPosition[arrayImages][1][1]
                        group.add(img(src=images, id=idImages, style="left:" + str(positionImagesX) + 'px;' + " top: " + str(positionImagesY) + 'px;'))
                    
                    container += group

            Html_file = open(formatsSize + "/" + "index.html", "w")
            Html_file.write(doc.render(pretty=True))
            Html_file.close()

def generateCss(content):

    for contFormatSize in range(0, len(content["formatsInfo"])):
        formatsSize = content["formatsInfo"][contFormatSize][0]
        splitFormatsSize = formatsSize.split('x')
        width = splitFormatsSize[0]
        height = splitFormatsSize[1]
        timeDelayIn = 0
        timeDelayOut = 0
        timeRead = 3000
        css = ''' 
        * {
            margin: 0;
            padding: 0;
        }
        
        #container {
	        position: relative;
            width: ''' + width + '''px;
	        height: ''' + height + '''px;
	        border: 1px solid #000;
	        overflow: hidden;
	        background: #fff;
	        cursor: pointer;
        }
    
        div, img {
            position: absolute;
            top: 0;
            left: 0;
        }
        
        div {
            width: 100%;
            height: 100%;
        }
    '''

        for groups in range(len(content["formatsInfo"][contFormatSize][1]) -1, -1, -1):
            group = content["formatsInfo"][contFormatSize][1][groups][0]
            if group != 'static':
                timeDelayOut += timeRead

                if groups > 0:
                    css += '''
                    #''' + group + ''' {
                    animation: inGroup 400ms ease-out ''' + str(timeDelayIn) + '''ms 1 normal forwards,
                                outGroup 400ms ease ''' + str(timeDelayOut) + '''ms 1 normal forwards;
                    }\n'''
                else:
                    css += '''
                    #''' + group + ''' {
                    animation: inGroup 400ms ease-out ''' + str(timeDelayIn) + '''ms 1 normal forwards;
                    }\n'''

                animation = '''
                @keyframes inGroup {
                    from {opacity: 0}
                    to {opacity: 1}
                }
                @keyframes outGroup {
                    from {opacity: 1}
                    to {opacity: 0}
                }'''

                timeDelayIn += timeRead

        cssFile = open(formatsSize + "/" + "style.css", "w")
        cssFile.write(css + animation)
        cssFile.close()


def removeFolders(pathFolder):
    shutil.rmtree(pathFolder, ignore_errors=True)


def createJson(nameOutput, content):
    try:
        to_unicode = unicode
    except NameError:
        to_unicode = str

    with io.open(nameOutput, 'w', encoding='utf8') as outfile:
        str_ = json.dumps(content, indent=4, sort_keys=True, separators=(',', ': '), ensure_ascii=False)
        outfile.write(to_unicode(str_))


def loadJson(pathFile):
    with open(pathFile, 'r') as f:
        array = json.load(f)


def getArrayFormatFilePath(arrayNamesWithoutExtensionPsd):
    arrayFormatPath = []
    for pathPsd in arrayNamesWithoutExtensionPsd:
        arrayPathPsd = pathPsd.split('\\')
        arrayFormatPath.append(arrayPathPsd[len(arrayPathPsd) - 1])
    return arrayFormatPath


def returnArrayPathPsdsInTheFolder(pathPsds):
    extension = '.psd'
    path = [os.path.join(pathPsds, name) for name in os.listdir(pathPsds)]
    files = [arq for arq in path if os.path.isfile(arq)]
    psds = [arq for arq in files if arq.lower().endswith(extension)]
    return psds


def removeExtensionPsd(arrayPathPsds):
    pathPsdWithouExtension = []
    for namePsd in arrayPathPsds:
        pathPsdWithouExtension.append(os.path.splitext(namePsd)[0])
    return pathPsdWithouExtension


def askAndReturnStringPathPsd():
    psdPath = input('Informe o caminho que contém todos os PSDS:')
    return psdPath


def returnArrayOpenPsd(arrayNamePsdInTheFolder):
    psds = []
    for namePsd in arrayNamePsdInTheFolder:
        psds.append(PSDImage.open(namePsd))
    return psds


def removeAccents(stringName):
    return (unidecode(stringName))


def removeWhitespace(stringName):
    stringNameWithoutWhitespace = re.sub("\s+", '-', stringName)
    return stringNameWithoutWhitespace


def exportImagesFromPsd(arrayPsds, pathCompleteImagensExport, content):
    arrayPathImagesExport = []
    extensionImage = '.png'
    contPsdsOpen = 0
    for psdOpen in arrayPsds:
        for layer in list(psdOpen.descendants(include_clip=True)):
            if layer.has_pixels():
                nameImages = layer.name + extensionImage
                nameImages = removeWhitespace(nameImages)
                nameImages = removeAccents(nameImages)
                layerImage = layer.topil()
                pathExport = pathCompleteImagensExport[contPsdsOpen] + '/' + nameImages
                layerImage.save(pathExport)
                arrayPathImagesExport.append(pathExport)

        contPsdsOpen += 1
    return arrayPathImagesExport


def returnArrayInfoFormats(arrayPsds, pathCompleteImagensExport, content):
    objectInfoPsd = {"formats": [], "frames": [], "layersInGroup": [], "layers": []}
    extensionImages = '.png'
    contAllPsds = 0

    for psdOpen in arrayPsds:
        objectInfoPsd["frames"] = []
        objectInfoPsd["layers"] = []
        
        for layer in psdOpen:
            nameLayer = layer.name + extensionImages
            nameLayer = removeWhitespace(nameLayer)
            nameLayer = removeAccents(nameLayer)
            
            if layer.is_group():
                objectInfoPsd["layersInGroup"] = []
                             
                for layersInGroup in reversed(list(layer.descendants(include_clip = True))):
                    layersInGroupName = layersInGroup.name + extensionImages
                    layersInGroupName = removeWhitespace(layersInGroupName)
                    layersInGroupName = removeAccents(layersInGroupName)
                    layersInGroupPosition = layersInGroup.offset
                    objectInfoPsd["layersInGroup"].append([layersInGroupName, layersInGroupPosition])
                
                nameGroup = layer.name
                nameGroup = removeWhitespace(nameGroup)
                nameGroup = removeAccents(nameGroup)
                
                objectInfoPsd["frames"].append([nameGroup, objectInfoPsd["layersInGroup"]])
                
            else:
                objectInfoPsd["layers"].append([nameLayer, layer.offset])
        
        if len(objectInfoPsd["layers"]) != 0:
            objectInfoPsd["frames"].append(['static', objectInfoPsd["layers"]])

        objectInfoPsd["formats"].append([content["createdFoldersName"][contAllPsds], objectInfoPsd["frames"]])
        
        contAllPsds += 1
        
    return objectInfoPsd["formats"]

def createPaste(pathPsds):
    for nameFolder in pathPsds:
        try:
            os.mkdir(nameFolder)
        except OSError:
            removeFolders(nameFolder)
            os.mkdir(nameFolder)
        else:
            print("Pasta criada com sucesso! Caminho da pasta: " + nameFolder)


start()
