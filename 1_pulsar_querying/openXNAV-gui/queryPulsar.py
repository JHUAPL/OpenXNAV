from psrqpy import QueryATNF


class PulsarDatabase():
	def __init__(self, **kwargs):
		query = QueryATNF()
		self.db = query.pandas

	def full_database(self):
		return self.db
	
	def query(self, x, y, r):
		print(x)
		print(y)
		print(r)
		c = [x, y, r]
		# result = QueryATNF(coord1=x, coord2=y, radius=r)
		result = QueryATNF(params=['JNAME', 'PSRJ','PEPOCH', 'DECJ', 'RAJD'], circular_boundary=c)
		return result.pandas


def formatPulsarName(p_name):
	name_split = p_name.split('+', 2)
	if len(name_split) < 2: 
		name_split = p_name.split('-', 2)
	if len(name_split) < 2: 
		p_name = name_split[0]
	else: 
		p_name = name_split[0] + "_" + name_split[1]
	return p_name

class Pulsar(): 
	def __init__(self, p_name, epoch, dec, right_a, ref_frame='J2000'):
		self.p_name = p_name
		self.epoch = epoch
		self.dec = dec
		self.right_a = right_a
		self.ref_frame = ref_frame

		self.ra_per_yr = 0
		self.dec_per_yr = 0
		self.parallax = 0
		self.magnitude = None
		self.rv = '0.0000000000000000e+00'
		self.p_id = 0

	def saveToFile(self, root_directory):
		# parse name
		self.p_name = formatPulsarName(self.p_name)


		# generate lines for file
		##
		lines = ['stk.v.12.0\n', 'WrittenBy    OpenXNAV\n\n', 'BEGIN Star\n\n']
		lines.append('    Name		 ' + self.p_name + '\n\n')
		lines.append('    BEGIN PathDescription\n\n')

		lines.append('        Epoch		  ' + str(self.epoch) + '\n')

		lines.append('        RefFrame		 ' + str(self.ref_frame) + '\n')

		lines.append('        RightAscension		  ' + str(self.right_a) + '\n')

		lines.append('        Declination		  ' + str(self.dec) + '\n')

		# PMElong ?
		lines.append('        ProperMotionRAPerYr		 ' + str(self.ra_per_yr) + '\n')

		# PMElat ?
		lines.append('        ProperMotionDecPerYr		 ' + str(self.dec_per_yr) + '\n')

		lines.append('        Parallax		  ' + str(self.parallax) + '\n')

		# VTrans ? 
		lines.append('        RadialVelocity		  ' + str(self.rv) + '\n\n')

		lines.append('    END PathDescription\n\n')
		lines.append('    BEGIN PhysicalData\n\n')

		lines.append('        Magnitude		  ' + str(self.magnitude) + "\n\n")

		lines.append('    END PhysicalData\n\n')
		lines.append('    BEGIN IdentityData\n\n')

		lines.append('        Id		 ' + str(self.p_id) + "\n\n")

		lines.append('    END IdentityData\n\n\n')

		lines.append('    BEGIN Extensions\n\n')

		lines.append('        BEGIN ExternData\n')
		lines.append('        END ExternData\n\n')

		lines.append('        BEGIN ADFFileData\n')
		lines.append('        END ADFFileData\n\n')

		lines.append('        BEGIN AccessConstraints\n')
		lines.append('            LineOfSight IncludeIntervals\n\n')
		lines.append('            UsePreferredMaxStep No\n')
		lines.append('            PreferredMaxStep 360\n')
		lines.append('        END AccessConstraints\n\n')

		lines.append('        BEGIN Desc\n')
		lines.append('        END Desc\n\n')

		lines.append('        BEGIN Crdn\n')
		lines.append('        END Crdn\n\n')

		lines.append('        BEGIN Graphics\n\n')

		lines.append('            BEGIN Attributes\n\n')
		lines.append('                MarkerColor		 #00ff00\n')
		lines.append('                LabelColor		 #00ff00\n')
		lines.append('                MarkerStyle		 2\n')
		lines.append('                FontStyle		 0\n\n')
		lines.append('            END Attributes\n\n')

		lines.append('            BEGIN Graphics\n\n')
		lines.append('                Show		 On\n')
		lines.append('                Inherit		 On\n')
		lines.append('                ShowLabel		 On\n')
		lines.append('                ShowMarker		 On\n\n')
		lines.append('            END Graphics\n')
		lines.append('        END Graphics\n\n')

		lines.append('        BEGIN VO\n')
		lines.append('        END VO\n\n')
		lines.append('    END Extensions\n\n')
		lines.append('END Star')

		filename = root_directory + self.p_name + ".st"
		with open(filename, 'w') as f:
			for line in lines:
				f.write(line)
		f.close()
