# WriteArdbXML.py
# Copyright 2006 Neil Muller <drnlmuller+sutekh@gmail.com>
# Based off the Anarach Revolt Deck Builder xml support,
# ARDB (c) Francios Gombalt, Christoph Boget, Ville Virta and Vincent Ripoll
# GPL - see COPYING for details

"""
Give a list of Abstract Cards in a set, write a XML file compatable with
the Anarch Revolt Deck Builder
"""

from sutekh.SutekhObjects import IAbstractCard
from xml.dom.ext import PrettyPrint
from xml.dom.minidom import getDOMImplementation
import time

class WriteArdbXML(object):

    def genDoc(self,sSetName,sAuthor,sDescription,dCards):
        """
        Creates the actual XML document into memory. Allows for conversion
        to HTML without using a Temporary file
        """
        oDoc = getDOMImplementation().createDocument(None,'deck',None)

        oDeckElem = oDoc.firstChild
        sDateWritten=time.strftime('%Y-%m-%d',time.localtime())
        oDeckElem.setAttribute('generator',"Sutekh [pre-release]")
        oDeckElem.setAttribute('formatVersion',"-TODO-1.0") # Claim same version as recent ARDB
        oDeckElem.setAttribute('databaseVersion',"Sutekh-20070701")
        oNameElem=oDoc.createElement('name')
        oNameElem.appendChild(oDoc.createTextNode(sSetName))
        oDeckElem.appendChild(oNameElem)
        oAuthElem=oDoc.createElement('author')
        oAuthElem.appendChild(oDoc.createTextNode(sAuthor))
        oDeckElem.appendChild(oAuthElem)
        oDescElem=oDoc.createElement('description')
        oDescElem.appendChild(oDoc.createTextNode(sDescription))
        oDeckElem.appendChild(oDescElem)
        oDateElem=oDoc.createElement('date')
        oDateElem.appendChild(oDoc.createTextNode(sDateWritten))
        oDeckElem.appendChild(oDateElem)

        (dVamps,iCryptSize,iMin,iMax,fAvg)=self.extractCrypt(dCards)
        (dLib,iLibSize)=self.extractLibrary(dCards)

        oCryptElem = oDoc.createElement('crypt')
        oCryptElem.setAttribute('size',str(iCryptSize))
        oCryptElem.setAttribute('min',str(iMin))
        oCryptElem.setAttribute('max',str(iMax))
        oCryptElem.setAttribute('avg',str(fAvg))
        oDeckElem.appendChild(oCryptElem)
        for tKey, iNum in dVamps.iteritems():
            iId, sName = tKey
            oCard=IAbstractCard(sName)
            oCardElem = oDoc.createElement('vampire')
            # This won't match the ARDB ID's, unless by chance.
            # It looks like that should not be an issue as ARDB will
            # use the name if the IDs don't match
            oCardElem.setAttribute('databaseID',str(iId))
            oCardElem.setAttribute('count',str(iNum))
            # FIXME: It's unclear to me what values ARDB uses here, but
            # these are fine for the xml2html conversion, and look meaningful
            oAdvElem=oDoc.createElement('adv')
            oNameElem=oDoc.createElement('name')
            # FIXME: How does ARDB handle titles and sects?
            # title is mentioned in the deck2html.xsl file, so
            # that should be there somehow. Relook at this
            if oCard.level is not None:
                oAdvElem.appendChild(oDoc.createTextNode("(Advanced)"))
                # This is a bit hackish
                oNameElem.appendChild(oDoc.createTextNode(\
                        sName.replace(' (Advanced)','')))
            else:
                oNameElem.appendChild(oDoc.createTextNode(sName))
            oCardElem.appendChild(oAdvElem)
            oCardElem.appendChild(oNameElem)
            oDiscElem=oDoc.createElement('disciplines')
            sDisciplines=self.getDisc(oCard)
            oDiscElem.appendChild(oDoc.createTextNode(sDisciplines))
            oCardElem.appendChild(oDiscElem)
            aClan=[x.name for x in oCard.clan]
            oClanElem=oDoc.createElement('clan')
            oClanElem.appendChild(oDoc.createTextNode(aClan[0]))
            oCardElem.appendChild(oClanElem)
            oCapElem=oDoc.createElement('capacity')
            oCapElem.appendChild(oDoc.createTextNode(str(oCard.capacity)))
            oCardElem.appendChild(oCapElem)
            oGrpElem=oDoc.createElement('group')
            oGrpElem.appendChild(oDoc.createTextNode(str(oCard.group)))
            oCardElem.appendChild(oGrpElem)
            # Skipping titles for the moment, as
            # I don't feel like trying to scan the text for that here
            oTextElem=oDoc.createElement('text')
            oTextElem.appendChild(oDoc.createTextNode(oCard.text))
            oCardElem.appendChild(oTextElem)
            oCryptElem.appendChild(oCardElem)

        oLibElem = oDoc.createElement('library')
        oLibElem.setAttribute('size',str(iLibSize))
        oDeckElem.appendChild(oLibElem)
        for tKey, iNum in dLib.iteritems():
            iId, sName = tKey
            oCard=IAbstractCard(sName)
            oCardElem = oDoc.createElement('card')
            oCardElem.setAttribute('databaseID',str(iId))
            oCardElem.setAttribute('count',str(iNum))
            oNameElem=oDoc.createElement('name')
            oNameElem.appendChild(oDoc.createTextNode(sName))
            oCardElem.appendChild(oNameElem)
            if oCard.costtype is not None:
                oCostElem=oDoc.createElement('cost')
                oCostElem.appendChild(oDoc.createTextNode( \
                        str(oCard.cost)+" "+oCard.costtype))
                oCardElem.appendChild(oCostElem)
            if len(oCard.clan)>0:
                # ARDB also strores things like "requires a prince"
                # we don't so to bad
                oReqElem=oDoc.createElement('requirement')
                aClan=[x.name for x in oCard.clan]
                oReqElem.appendChild(oDoc.createTextNode("/".join(aClan)))
                oCardElem.appendChild(oReqElem)
            # Looks like it should be the right thing, but may not
            aTypes=[x.name for x in oCard.cardtype]
            sType="/".join(aTypes)
            oTypeElem=oDoc.createElement('type')
            oTypeElem.appendChild(oDoc.createTextNode(sType))
            oCardElem.appendChild(oTypeElem)
            # Not sure if this does quite the right thing here
            sDisciplines=self.getDisc(oCard)
            if sDisciplines!='':
                oDiscElem=oDoc.createElement('disciplines')
                oDiscElem.appendChild(oDoc.createTextNode(sDisciplines))
                oCardElem.appendChild(oDiscElem)
            oTextElem=oDoc.createElement('text')
            oTextElem.appendChild(oDoc.createTextNode(oCard.text))
            oCardElem.appendChild(oTextElem)
            oLibElem.appendChild(oCardElem)
        return oDoc

    def write(self,fOut,sSetName,sAuthor,sDescription,dCards):
        """
        Takes filename, deck details and a dictionary of cards, of the form
        dCard[(id,name)]=count
        """
        oDoc=self.genDoc(sSetName,sAuthor,sDescription,dCards)
        PrettyPrint(oDoc,fOut)

    def getDisc(self,oCard):
        aDisc=[]
        if not len(oCard.discipline) ==  0:
            for oP in oCard.discipline:
                if oP.level == 'superior':
                    aDisc.append(oP.discipline.name.upper())
                else:
                    aDisc.append(oP.discipline.name)
            aDisc.sort() # May not be needed
            return " ".join(aDisc)
        else:
            return ""

    def extractCrypt(self,dCards):
        iCryptSize=0
        iMax=0
        iMin=75
        fAvg=0.0
        dVamps={}
        for tKey,iCount in dCards.iteritems():
            iId,sName = tKey
            oCard=IAbstractCard(sName)
            aTypes=[x.name for x in oCard.cardtype]
            if aTypes[0]=='Vampire':
                dVamps[tKey]=iCount
                iCryptSize+=iCount
                fAvg+=oCard.capacity*iCount
                if oCard.capacity>iMax:
                    iMax=oCard.capacity
                if oCard.capacity<iMin:
                    iMin=oCard.capacity
        if iCryptSize>0:
            fAvg=round(fAvg/iCryptSize,2)
        if iMin==75:
            iMin=0
        return (dVamps,iCryptSize,iMin,iMax,fAvg)

    def extractLibrary(self,dCards):
        iSize=0
        dLib={}
        for tKey,iCount in dCards.iteritems():
            iId,sName = tKey
            oCard=IAbstractCard(sName)
            aTypes=[x.name for x in oCard.cardtype]
            if aTypes[0]!='Vampire':
                dLib[tKey]=iCount
                iSize+=iCount
        return (dLib,iSize)
