# Copyright (c) Sergiy Migdalskiy , migdalskiy@hotmail.com. All Rights Reserved.


import os, getopt,datetime,sys,fnmatch,pyexiv2


def isImageName(f):
	return fnmatch.fnmatch(f, '*.jpg') or fnmatch.fnmatch(f, '*.dng') or fnmatch.fnmatch(f, '*.cr2') or fnmatch.fnmatch(f, '*.mov')

if __name__ == "__main__":
	try:
		(opts, _) = getopt.getopt(sys.argv[1:], 'd:frs')
	except getopt.GetoptError:
		print ('Run: scatter -d <directory> [-f] [-r] [-s]')
		exit()
	dir=os.getcwd()
	dryRun = True
	subDir='..'
	forceMove = False
	for (k, v) in opts:
		if(k=='-d'):
			dir=v
		elif( k=='-f'):
			forceMove = True
			dryRun=False
		elif( k== '-r'):
			dryRun=False
		elif(k=='-s'):
			subDir=''
		dir = os.path.normpath(dir)
	print ('listing dir "{0}"'.format(dir))
	files = [f for f in os.listdir(dir) if isImageName(f) and os.path.isfile(os.path.join(dir,f))]
	print ("Processing {0} files".format(len(files)))
	bMove = True
	statistics = dict()
	moveList = []
	noExifDateTag=0
	for f in files:
		srcFile = os.path.normpath(os.path.join(dir,f))
		try:
			metadata = pyexiv2.ImageMetadata(srcFile)
			metadata.read()
		except:
			metadata=[]

		if 'Exif.Image.DateTime' in metadata:
			dt=metadata['Exif.Image.DateTime'].value
		else:
			dt = datetime.datetime.fromtimestamp( os.stat(srcFile).st_mtime )
			noExifDateTag=noExifDateTag+1
		destDir = os.path.normpath( os.path.join(dir,subDir,dt.strftime('%Y-%m-%d')) )
		if(destDir != dir):
			if destDir not in statistics:
				statistics[destDir] = 1
			else:
				statistics[destDir] = 1 + statistics[destDir]
			destFile = os.path.normpath(os.path.join(destDir,f))
			if(os.path.isfile(destFile)):
				print ('File Already Exists: '+destFile)
				bMove = False
			elif(os.path.isdir(destFile)):
				print('Dir in place of file: ' + destFile)
				bMove = False
			else:
				moveList.append((srcFile,destFile))

	if noExifDateTag > 0:
		print("{0} of {1} files had NO EXIF date tag".format(noExifDateTag,len(files)))

	if(len(moveList)==0):
		print("All files already in their right directory. No files were moved")
	else:
		print ("Starting move file operation for {0} files, skipping {1} files:".format(len(moveList),len(files)-len(moveList)))
		for (dir,count) in statistics.iteritems():
			print ("{0}\t{1}".format(count, dir ) )

		if(dryRun):
			print("Dry Run complete. Run with -r to actually perform move operation")
		else:
			if bMove or forceMove:
				for (srcFile,destFile) in moveList:
					destDir = os.path.dirname(destFile)
					if not os.path.isdir(destDir):
						os.mkdir(destDir)
					try:
						os.rename(srcFile, destFile)
					except OSError as e:
						print "Error moving " + srcFile + " to " + destFile
						print e
						exit()
				print "Done"
			else:
				print "Skipping " + len( moveList ) + " file moves. Please resolve warnings or run with -f"
