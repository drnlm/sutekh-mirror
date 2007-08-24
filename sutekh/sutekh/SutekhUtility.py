# SutekhUtility.py
# Copyright 2006 Simon Cross <hodgestar@gmail.com>
# Minor modifications copyright 2006 Neil Muller <drnlmuller+sutekh@gmail.com>
# GPL - see COPYING for details
# Misc Useful functions needed in several places. Mainly to do with database
# management. Seperated out from SutekhCli and other places, NM, 2006

from sutekh.core.SutekhObjects import VersionTable, FlushCache
from sutekh.core.DatabaseVersion import DatabaseVersion
from sutekh.io.WhiteWolfParser import WhiteWolfParser
from sutekh.io.RulingParser import RulingParser
from sqlobject import sqlhub
import codecs, tempfile, os, sys

def refreshTables(aTables,oConn,**kw):
    aTables.reverse()
    for cCls in aTables:
        cCls.dropTable(ifExists=True,connection=oConn)
    aTables.reverse()
    oVerHandler = DatabaseVersion(oConn)
    if not oVerHandler.setVersion(VersionTable,VersionTable.tableversion,oConn):
        return False
    for cCls in aTables:
        cCls.createTable(connection=oConn)
        if not oVerHandler.setVersion(cCls, cCls.tableversion,oConn):
            return False
    return True

def readWhiteWolfList(sWwList):
    FlushCache()
    oldConn = sqlhub.processConnection
    sqlhub.processConnection = oldConn.transaction()
    oP = WhiteWolfParser()
    fIn = codecs.open(sWwList,'rU','cp1252')
    for sLine in fIn:
        oP.feed(sLine)
    fIn.close()
    sqlhub.processConnection.commit()
    sqlhub.processConnection = oldConn

def readRulings(sRulings):
    FlushCache()
    oldConn = sqlhub.processConnection
    sqlhub.processConnection = oldConn.transaction()
    oP = RulingParser()
    fIn = codecs.open(sRulings,'rU','cp1252')
    for sLine in fIn:
        oP.feed(sLine)
    fIn.close()
    sqlhub.processConnection.commit()
    sqlhub.processConnection = oldConn

def genTempFile(sBaseName,sDir):
    """Simple wrapper around tempfile creation - generates the name and closes
       the file"""
    (fd, sFilename) = tempfile.mkstemp('.xml',sBaseName,sDir)
    # This may not be nessecary, but the available documentation
    # suggests that, on Windows NT anyway, leaving the file open will
    # cause problems when writePhysicalCards tries to reopen it
    os.close(fd)
    # There is a race condition here, but since Sutekh should not be running
    # with elevated priveleges, this should never be a security issues
    # The the race requires something to delete and replace the tempfile,
    # I don't see it being triggered accidently
    return sFilename

def genTempdir():
    sTempdir = tempfile.mkdtemp('dir','sutekh')
    return sTempdir

def safeFilename(sFilename):
    """Replace potentially dangerous and annoying characters in the name -
       used to automatically generate sensible filenames from card set names"""
    sSafeName = sFilename
    sSafeName = sSafeName.replace(" ","_") # I dislike spaces in filenames
    sSafeName = sSafeName.replace("/","_") # Prevented unexpected filesystem issues
    sSafeName = sSafeName.replace("\\","_") # ditto for windows
    return sSafeName

def prefsDir(sApp):
    """Return a suitable directory for storing preferences and other application data.
       """
    if sys.platform.startswith("win") and "APPDATA" in os.environ:
        return os.path.join(os.environ["APPDATA"],sApp)
    else:
        return os.path.join(os.path.expanduser("~"),".%s" % sApp.lower())

def ensureDirExists(sDir):
    """Check that a directory exists and create it if it doesn't.
       """
    if os.path.exists(sDir):
        assert os.path.isdir(sDir)
    else:
        os.makedirs(sDir)

def sqliteUri(sPath):
    """Create an SQLite db URI from the path to the db file.
       """
    sDbFile = sPath.replace(os.sep,"/")

    sDrive, sRest = os.path.splitdrive(sDbFile)
    if sDrive:
        sDbFile = "/" + sDrive.rstrip(':') + "|" + sRest
    else:
        sDbFile = sRest

    return "sqlite://" + sDbFile

