from struct import pack

import MySQLdb as mysql

import logger


_connection = None


class Airport(object):
    """
    The Airport class represents a single airport.
    It is just a utility class to make operations on the database easier.
    """

    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.city = kwargs['city']
        self.country = kwargs['country']
        self.iata = kwargs['iata']
        self.icao = kwargs['icao']
        self.latitude = float(kwargs['latitude'])
        self.longitude = float(kwargs['longitude'])
        self.altitude = int(kwargs['altitude'])

    def is_valid(self):
        """
        Return true if all params of the airport are O.K.
        """
        return not (self.latitude == 0.0 and self.longitude == 0.0)

    def to_raw_bytes(self):
        """
        Convert the airport data to raw bytes, format compatible with the database.
        The format is as follows:
        128 bytes of name (string);
        128 bytes of city (string);
        128 bytes of country name (string);
        8 bytes of iata code (string);
        8 bytes of icao code (string);
        4 bytes of latitude (float);
        4 bytes of longitude (float);
        4 bytes of altitude (int).
        All strings are null-terminated.
        """
        return pack('128s128s128s8s8sffi', self.name, self.city, self.country, self.iata, self.icao, self.latitude,
                    self.longitude, self.altitude)


def _db_connect(host, user, passwd, db, unix_socket=None):
    global _connection
    _connection = mysql.connect(host=host, user=user, passwd=passwd, db=db, unix_socket=unix_socket)


def fetch_airports(config, output_file='WorldAirports.db'):
    """
    Fetch all airports from the database and generate the WorldAirports.db file.
    @type config: ConfigParser.ConfigParser instance
    @param config: User config.
    @param output_file: Output file name (default: WorldAirports.db).
    """
    if _connection is None:
        _db_connect(config.get('Database', 'host'), config.get('Database', 'user'), config.get('Database', 'passwd'),
                    config.get('Database', 'db'),
                    None if not config.has_option('Database', 'unix_socket') else config.get('Database', 'unix_socket'))

    airports = []
    c = _connection.cursor()
    query = 'SELECT name, city, country, iata, icao, latitude, longitude, altitude FROM %s' % \
            config.get('Database', 'airports_table_name')
    c.execute(query)
    for name, city, country, iata, icao, latitude, longitude, altitude in c.fetchall():
        ap = Airport(name=name, city=city, country=country, iata=iata, icao=icao, latitude=latitude,
                     longitude=longitude, altitude=altitude)
        if ap.is_valid():
            airports.append(ap)
        else:
            logger.info('Skipping %s as invalid airport' % ap.icao)

    # write to the database
    db_out = open(output_file, 'wb')
    db_out.write(pack('i', len(airports)))
    i = 0
    for ap in airports:
        db_out.write(ap.to_raw_bytes())
        i += 1
    db_out.close()
    logger.info('Wrote %i airports' % i)
