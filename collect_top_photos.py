# -*- coding: utf-8 -*-

import sys, os, shutil, subprocess, mmap, exifread, xattr, biplist, re, hashlib

GOOD_RATING = 5
GOOD_RATING_WITH_KEYWORDS = 4
GOOD_KEYWORDS = {"I", "Me"}

def readExif(filename):
    with open(filename, 'rb') as file:
        tags = exifread.process_file(file)
        tags.pop('JPEGThumbnail', None)
        return tags

def readXmpData(filename):
    with open(filename,"rb") as file:
        fileString = mmap.mmap(file.fileno(), 0, access=mmap.PROT_READ)
        xmp_start = fileString.find('<x:xmpmeta')
        xmp_end = fileString.find('</x:xmpmeta>')
        if xmp_start != xmp_end:
            xmpString = fileString[xmp_start:xmp_end + 12]
            return xmpString

def readXmpRating(filename):
    xmpData = readXmpData(filename)
    if xmpData:
        xmpRatingPos = xmpData.find('xmp:Rating')
        if xmpRatingPos != -1:
            rating = xmpData[(xmpRatingPos + len('xmp:Rating="')):(xmpRatingPos + len('xmp:Rating="#'))]
            return int(rating)

def readXmpKeywords(filename):
    xmpData = readXmpData(filename)
    if xmpData:
        xmp_start = xmpData.find('<dc:subject')
        xmp_end = xmpData.find('</dc:subject>')
        if xmp_start != xmp_end:
            xmpString = xmpData[xmp_start:xmp_end + 13]
            return re.findall('<rdf:li>([^<]+)<\/rdf:li>', xmpString)

def readMetadataRating(filename):
    attribs = xattr.xattr(filename).items()
    for (key, value) in attribs:
        if u'kMDItemStarRating' in key:
            rating = biplist.readPlistFromString(value)
            return int(rating)

def readMetadataKeywords(filename):
    attribs = xattr.xattr(filename).items()
    for (key, value) in attribs:
        if u'com.apple.metadata:kMDItemOMUserTags' in key:
            keywords = biplist.readPlistFromString(value)
            return keywords

def dateFromExif(filename):
    exif = readExif(filename)
    dateExif = (filter(None, [exif.get('EXIF DateTimeOriginal', None), exif.get('EXIF DateTimeDigitized', None), exif.get('Image DateTime', None)]) or [None])[0]
    return dateExif

def filenameForPhoto(filename):
    dateExif = dateFromExif(filename)
    if dateExif == None:
        print 'ERROR: no Exif date properties in', filename
        return os.path.basename(filename)
    namePrefix = str(dateExif).split(' ')[0].replace(':', '-')
    return namePrefix + '_' + os.path.basename(filename)


sourcePhotos = []
sourcePath = sys.argv[1]
destPath = sys.argv[2]
print 'source path:', sourcePath
print 'destination path:', destPath
for (dirpath, dirnames, filenames) in os.walk(sourcePath):
    filesInDirectory = [os.path.join(dirpath, f) for f in filenames if (f.endswith('.jpg') or f.endswith('.JPG'))]
    sourcePhotos.extend(filesInDirectory)
print len(sourcePhotos), 'photos found'

goodPhotos = []
for i, f in enumerate(sourcePhotos):
    sys.stdout.write('\r')
    sys.stdout.write('processing {0} of {1} photos: {2}'.format(i + 1, len(sourcePhotos), f))
    sys.stdout.flush()

    rating = readXmpRating(f)
    if not rating:
        rating = readMetadataRating(f)
    if rating >= GOOD_RATING:
        goodPhotos.append(f)
    elif rating >= GOOD_RATING_WITH_KEYWORDS:
        keywords = readMetadataKeywords(f)
        if not keywords:
            keywords = readXmpKeywords(f)
        if keywords and GOOD_KEYWORDS.intersection(keywords):
            goodPhotos.append(f)

sys.stdout.write('\r')

print len(goodPhotos), 'photos with good ratings and keywords'

for sourceFilePath in goodPhotos:
    sourceHash = hashlib.md5(str(dateFromExif(sourceFilePath)))
    destFilePath = os.path.join(destPath, filenameForPhoto(sourceFilePath))
    if os.path.isfile(destFilePath):
        destHash = hashlib.md5(str(dateFromExif(destFilePath)))
        if sourceHash.hexdigest() != destHash.hexdigest():
            print 'ERROR: different photo already exists for:', sourceFilePath
        else:
            print 'skipped:', sourceFilePath
        continue
    shutil.copy2(sourceFilePath, destFilePath)
    exitcode = subprocess.call(['sips', '-Z', '2400', destFilePath], stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'))
    if exitcode == 0:
        print 'transferred:', sourceFilePath
    else:
        print 'ERROR: can\'t resize photo', destFilePath, ':', exitcode
