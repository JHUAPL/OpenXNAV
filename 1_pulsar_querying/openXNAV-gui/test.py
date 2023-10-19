from queryPulsar import PulsarDatabase


# from
# https://scipython.com/book/chapter-2-the-core-python-language-i/additional-problems/converting-decimal-degrees-to-deg-min-sec/
def deg_to_dms(deg, pretty_print=None, ndp=4):
    """Convert from decimal degrees to degrees, minutes, seconds."""

    m, s = divmod(abs(deg)*3600, 60)
    d, m = divmod(m, 60)
    if deg < 0:
        d = -d
    d, m = int(d), int(m)

    if pretty_print:
        if pretty_print=='latitude':
            hemi = 'N' if d>=0 else 'S'
        elif pretty_print=='longitude':
            hemi = 'E' if d>=0 else 'W'
        else:
            hemi = '?'
        return '{d:d}° {m:d}′ {s:.{ndp:d}f}″ {hemi:1s}'.format(
                    d=abs(d), m=m, s=s, hemi=hemi, ndp=ndp)

    return str(d) + ":" + str(m) + ":" + str(s)
    # return d, m, s

# run
if __name__ == '__main__':

	psrdb = PulsarDatabase()
	# db = psrdb.full_database()

	ra = 266.86	# lon
	dec = 65.64 	# lat

	rad = 15.0

	# query THE MOON
	# https://en.wikipedia.org/wiki/Moon
	print(psrdb.query('17:47:26', '65:38:24', rad))





