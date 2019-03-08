'''
def auto_line_calibrate():
	MINMIN = 0
	MINMAX = 1
	MAXMIN = 2
	MAXMAX = 3
	LINMIN = 4
	LINMAX = 5

	min_line_count = 99
	max_line_count = 0
	max_line_length = 0
	threshold_range = [0,0,0,0,0,0]
	minLineLength_range = [0,0,0,0,0,0]
	maxLineGap_range = [0,0,0,0,0,0]
	apertureSize_range = [0,0,0,0,0,0]

	image = cv2.imread("lines.png")
	# image = cv2.imread("lines.jpg")
	# image = cv2.imread("curveline.png")
	# image = cv2.imread("braccetto.jpg")
	image = imutils.resize(image, width=800)

	for apertureSize in range(3,8,1):
		for threshold in range(10,260,10):
			for minLineLength in range(10,260,10):
				for maxLineGap in range(10,260,10):
					gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
					blurred = cv2.GaussianBlur(gray, (1, 1), 0)
					edges = auto_canny(blurred)
					lines = cv2.HoughLinesP(edges, rho, theta, threshold, minLineLength, maxLineGap)
					if lines is None:
						continue
					line_count = len(lines)
					if (min_line_count >= line_count):
						if min_line_count == line_count:
							if threshold < threshold_range[MINMIN]:
								threshold_range[MINMIN] = threshold
							elif threshold > threshold_range[MINMAX]:
								threshold_range[MINMAX] = threshold

							if minLineLength < minLineLength_range[MINMIN]:
								minLineLength_range[MINMIN] = minLineLength
							elif minLineLength > minLineLength_range[MINMAX]:
								minLineLength_range[MINMAX] = minLineLength

							if maxLineGap < maxLineGap_range[MINMIN]:
								maxLineGap_range[MINMIN] = maxLineGap
							elif maxLineGap > maxLineGap_range[MINMAX]:
								maxLineGap_range[MINMAX] = maxLineGap

							if apertureSize < apertureSize_range[MINMIN]:
								apertureSize_range[MINMIN] = apertureSize
							elif apertureSize > apertureSize_range[MINMAX]:
								apertureSize_range[MINMAX] = apertureSize
						else:
							min_line_count = line_count
							threshold_range[MINMIN:MINMAX+1] = [threshold,threshold]
							minLineLength_range[MINMIN:MINMAX+1] = [minLineLength,minLineLength]
							maxLineGap_range[MINMIN:MINMAX+1] = [maxLineGap,maxLineGap]
							apertureSize_range[MINMIN:MINMAX+1] = [apertureSize,apertureSize]

						# print("threshold=[%d,%d], minLineLength=[%d,%d], maxLineGap=[%d,%d], apertureSize=[%d,%d], min_line_count=%d" % (threshold_range[MINMIN], threshold_range[MINMAX], minLineLength_range[MINMIN], minLineLength_range[MINMAX], maxLineGap_range[MINMIN], maxLineGap_range[MINMAX], apertureSize_range[MINMIN], apertureSize_range[MINMAX], min_line_count))

					if (max_line_count <= line_count):
						if max_line_count == line_count:
							if threshold < threshold_range[MAXMIN]:
								threshold_range[MAXMIN] = threshold
							elif threshold > threshold_range[MAXMAX]:
								threshold_range[MAXMAX] = threshold

							if minLineLength < minLineLength_range[MAXMIN]:
								minLineLength_range[MAXMIN] = minLineLength
							elif minLineLength > minLineLength_range[MAXMAX]:
								minLineLength_range[MAXMAX] = minLineLength

							if maxLineGap < maxLineGap_range[MAXMIN]:
								maxLineGap_range[MAXMIN] = maxLineGap
							elif maxLineGap > maxLineGap_range[MAXMAX]:
								maxLineGap_range[MAXMAX] = maxLineGap

							if apertureSize < apertureSize_range[MAXMIN]:
								apertureSize_range[MAXMIN] = apertureSize
							elif apertureSize > apertureSize_range[MAXMAX]:
								apertureSize_range[MAXMAX] = apertureSize
						else:
							max_line_count = line_count
							threshold_range[MAXMIN:MAXMAX+1] = [threshold,threshold]
							minLineLength_range[MAXMIN:MAXMAX+1] = [minLineLength,minLineLength]
							maxLineGap_range[MAXMIN:MAXMAX+1] = [maxLineGap,maxLineGap]
							apertureSize_range[MAXMIN:MAXMAX+1] = [apertureSize,apertureSize]

						# print("threshold=[%d,%d], minLineLength=[%d,%d], maxLineGap=[%d,%d], apertureSize=[%d,%d], max_line_count=%d" % (threshold_range[MAXMIN], threshold_range[MAXMAX], minLineLength_range[MAXMIN], minLineLength_range[MAXMAX], maxLineGap_range[MAXMIN], maxLineGap_range[MAXMAX], apertureSize_range[MAXMIN], apertureSize_range[MAXMAX], max_line_count))

					for x1,y1,x2,y2 in lines[0]:
						d = math.sqrt( math.pow((x2-x1),2) + math.pow((y2-y1),2) )
						if max_line_length <= d:
							if max_line_length == d:
								if threshold < threshold_range[LINMIN]:
									threshold_range[LINMIN] = threshold
								elif threshold > threshold_range[LINMAX]:
									threshold_range[LINMAX] = threshold

								if minLineLength < minLineLength_range[LINMIN]:
									minLineLength_range[LINMIN] = minLineLength
								elif minLineLength > minLineLength_range[LINMAX]:
									minLineLength_range[LINMAX] = minLineLength

								if maxLineGap < maxLineGap_range[LINMIN]:
									maxLineGap_range[LINMIN] = maxLineGap
								elif maxLineGap > maxLineGap_range[LINMAX]:
									maxLineGap_range[LINMAX] = maxLineGap

								if apertureSize < apertureSize_range[LINMIN]:
									apertureSize_range[LINMIN] = apertureSize
								elif apertureSize > apertureSize_range[LINMAX]:
									apertureSize_range[LINMAX] = apertureSize
							else:
								max_line_length = d
								threshold_range[LINMIN:LINMAX+1] = [threshold,threshold]
								minLineLength_range[LINMIN:LINMAX+1] = [minLineLength,minLineLength]
								maxLineGap_range[LINMIN:LINMAX+1] = [maxLineGap,maxLineGap]
								apertureSize_range[LINMIN:LINMAX+1] = [apertureSize,apertureSize]
							
							# print("threshold=[%d,%d], minLineLength=[%d,%d], maxLineGap=[%d,%d], apertureSize=[%d,%d], max_line_length=%d" % (threshold_range[LINMIN], threshold_range[LINMAX], minLineLength_range[LINMIN], minLineLength_range[LINMAX], maxLineGap_range[LINMIN], maxLineGap_range[LINMAX], apertureSize_range[LINMIN], apertureSize_range[LINMAX], max_line_length))

	print("\nthreshold=[%d,%d], minLineLength=[%d,%d], maxLineGap=[%d,%d], apertureSize=[%d,%d]\nmin_line_count=%d" % (threshold_range[MINMIN], threshold_range[MINMAX], minLineLength_range[MINMIN], minLineLength_range[MINMAX], maxLineGap_range[MINMIN], maxLineGap_range[MINMAX], apertureSize_range[MINMIN], apertureSize_range[MINMAX], min_line_count))

	print("\nthreshold=[%d,%d], minLineLength=[%d,%d], maxLineGap=[%d,%d], apertureSize=[%d,%d]\nmax_line_count=%d" % (threshold_range[MAXMIN], threshold_range[MAXMAX], minLineLength_range[MAXMIN], minLineLength_range[MAXMAX], maxLineGap_range[MAXMIN], maxLineGap_range[MAXMAX], apertureSize_range[MAXMIN], apertureSize_range[MAXMAX], max_line_count))

	print("\nthreshold=[%d,%d], minLineLength=[%d,%d], maxLineGap=[%d,%d], apertureSize=[%d,%d]\nmax_line_length=%d" % (threshold_range[LINMIN], threshold_range[LINMAX], minLineLength_range[LINMIN], minLineLength_range[LINMAX], maxLineGap_range[LINMIN], maxLineGap_range[LINMAX], apertureSize_range[LINMIN], apertureSize_range[LINMAX], max_line_length))

# auto_line_calibrate()
# exit()
'''