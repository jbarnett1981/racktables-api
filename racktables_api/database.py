# Database connection class imports
import pymysql
from flask import abort



def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

class RacktablesDB:
    def __init__(self, host, username, password, db):
        '''
        init
        '''
        self.host = host
        self.username = username
        self.password = password
        self.db = db
        self.conn = None

    def connect(self):
        '''
        Connect to Racktables DB
        '''
        if not self.conn:
            self.conn = pymysql.connect(host=self.host, user=self.username, passwd=self.password, db=self.db)
            self.cursor = self.conn.cursor()

    def close(self):
        if self.conn:
            self.conn.close()

    def sql_query(self, sql):
        '''
        sql query wrapper
        '''
        #Perform query and return JSON data
        cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        if type(sql) == list:
            for q in sql:
                cursor.execute(q)
        else:
            cursor.execute(sql)
        result = cursor.fetchall()
        return result

    def add_object(self, name, objtype_id=4):
        '''
        Create object
        '''
        sql = "insert into Object (id, name, label, objtype_id, asset_no, has_problems, comment) values (NULL,'%s',NULL,%s,NULL,'no',NULL)" % (name, objtype_id)
        self.cursor.execute(sql)
        self.conn.commit()

    def get(self, hostname):
        '''
        Get host info
        '''
        hostid = self.get_id(hostname)
        if hostid == None:
            abort(410)
        sql = "select id, name from Object where id='%s'" % hostid
        query = self.sql_query(sql)
        status = self.get_host_status(hostid)
        hwtype = self.get_host_hwtype(hostid)
        serial_no = self.get_host_serial_num(hostid)
        os_type = self.get_host_os(hostid)
        domain = self.get_host_domain(hostid)
        result = {'data': query}
        result['data'][0]['status'] = status
        result['data'][0]['hwtype'] = hwtype
        result['data'][0]['serial_no'] = serial_no
        result['data'][0]['os'] = os_type
        result['data'][0]['domain'] = domain
        # result['status'] = 200
        # out.status_code = 200
        return result

    def get_id(self, hostname):
        '''
        Returns the racktables object id for a given hostname or returns the id if already provided
        '''
        if is_number(hostname):
            sql = "select id from Object where id='%s'" % hostname
        else:
            sql = "select id from Object where name='%s'" % hostname
        try:
            result = self.sql_query(sql)
            return result[0]['id']
        except IndexError:
            #return "None" if host doesn't exist
            return None

    def get_host_status(self, hostid):
        '''
        Returns the Status for a particular hostname.
        '''
        sql = "select t2.dict_value status from AttributeValue t1 left join Dictionary t2 on t1.uint_value=t2.dict_key where t1.attr_id=10005 and t1.object_id='%s'" % hostid
        try:
            result = self.sql_query(sql)
            status = result[0]['status']
            return status
        except IndexError:
            return None

    def get_host_hwtype(self, hostid):
        ''' Returns hardware type for a specific hostname/id
        '''
        # query = self.cursor.execute("select distinct id,name, dict_value hw_type from Object t1 left join AttributeValue t2 on t1.id=t2.object_id left join TagStorage t3 on t1.id=t3.entity_id left join Dictionary t4 on t2.uint_value=t4.dict_key where t2.attr_id=2 and t1.id='%s'" % hostname)
        sql = "select distinct id,name, dict_value hw_type from Object t1 left join AttributeValue t2 on t1.id=t2.object_id left join TagStorage t3 on t1.id=t3.entity_id left join Dictionary t4 on t2.uint_value=t4.dict_key where t2.attr_id=2 and t1.id='%s'" % hostid
        try:
            result = self.sql_query(sql)
            status = result[0]['hw_type']
            return status
        except IndexError:
            return None

    def get_host_os(self, hostid):
        ''' Returns the OS Type for a given host id
        '''
        sql = "select t2.dict_value os_type from AttributeValue t1 left join Dictionary t2 on t1.uint_value=t2.dict_key where t1.attr_id=4 and t1.object_id='%s'" % hostid
        try:
            result = self.sql_query(sql)
            status = result[0]['os_type']
            return status
        except IndexError:
            return None

    def get_host_serial_num(self, hostid):
        ''' Returns the serial number in AttributeValue table from given host id
        '''
        sql = "select string_value from AttributeValue where object_id='%s' and attr_id=1" % hostid
        try:
            result = self.sql_query(sql)
            status = result[0]['string_value']
            return status
        except IndexError:
            return None

    def get_serial_num_exist(self, serial_num):
        '''
        Verifies whether a given serial number exists in the database
        '''
        sql = "select * from AttributeValue where string_value='%s' and attr_id=1;" % serial_num
        try:
            result = self.sql_query(sql)
            serial_exists = result[0]['string_value']
            return serial_exists
        except IndexError:
            return None

    def get_status_id(self, statusname):
        '''
        Returns the status ID for a given string in the Dictionary.
        '''
        # Get the dict_key for the desired status
        sql = "select dict_key from Dictionary where chapter_id=10003 and dict_value='%s'" % statusname
        result = self.sql_query(sql)
        try:
            status_id = result[0]['dict_key']
            return status_id
        except IndexError:
            return None

    def set_host_status(self, hostid, statusname):
        '''
        Sets the Status for a particular hostname.
        '''
        # Get Status ID
        status_id = self.get_status_id(statusname)
        if status_id == None:
            abort(410)
        # Get status: if None insert record, otherwise update existing
        try:
            status_exists = self.get_host_status(hostid)
        except TypeError:
            pass
        if status_exists == None:
            self.cursor.execute("insert into AttributeValue (object_id, object_tid, attr_id, string_value, uint_value, float_value) values (%s,4,10005,NULL,%s,NULL) on duplicate key update object_id=object_id""", (hostid, status_id))
        else:
            self.cursor.execute("update AttributeValue set uint_value=%s where attr_id=10005 and object_id=%s""", (status_id, hostid))
        self.conn.commit()

    def set_host_serial_num(self, hostid, serial_num):
        '''
        Update the serial number of a given host id. raise ResourceAlreadyExists if serial_no already exists.
        '''
        serial_exists = self.get_serial_num_exist(serial_num)
        if serial_exists:
            abort(409)
        try:
            serial_exists = self.get_host_serial_num(hostid)
        except TypeError:
            serial_exists = None
        if serial_exists == None:
            self.cursor.execute("insert into AttributeValue (object_id, object_tid, attr_id, string_value, uint_value, float_value) values (%s,4,1,%s,NULL,NULL) on duplicate key update object_id=object_id", (hostid, serial_num))
        else:
            self.cursor.execute("update AttributeValue set string_value=%s where attr_id=1 and object_id=%s", (serial_num, hostid))
        self.conn.commit()

    def get_domain_id(self, domain):
        '''
        Retrieves the racktables id/name for a given domain or None if not found
        '''
        if is_number(domain):
            sql = "select dict_key, dict_value from Dictionary where chapter_id=10002 and dict_key=%s" % domain
        else:
            sql = "select dict_key, dict_value from Dictionary where chapter_id=10002 and dict_value='%s'" % domain
        result = self.sql_query(sql)
        try:
            domain_id = result[0]['dict_key']
            return domain_id
        except IndexError:
            return None

    def get_host_domain(self, hostid):
        ''' Gets the host's configured domain or returns None if not set
        '''
        sql = "select t1.object_id,t2.dict_key,t2.dict_value from AttributeValue t1 left join Dictionary t2 on t1.uint_value=t2.dict_key where t1.attr_id=10002 and object_id='%s'" % hostid
        result = self.sql_query(sql)
        try:
            host_domain = result[0]['dict_value']
            return host_domain
        except IndexError:
            return None

    def set_host_domain(self, hostid, domain):
        '''
        Configures domain attribute on hostname
        '''
        domain_id = self.get_domain_id(domain)
        if domain_id == None:
            abort(410)
        try:
            domain_already_configured = self.get_host_domain(hostid)
        except TypeError:
            domain_already_configured = None
        if domain_already_configured:
            self.cursor.execute("update AttributeValue set uint_value=%s where attr_id=10002 and object_id=%s", (domain_id, hostid))
        else:
            self.cursor.execute("insert into AttributeValue (object_id, object_tid, attr_id, string_value, uint_value, float_value) values (%s,4,10002,NULL,%s,NULL) on duplicate key update object_id=object_id", (hostid, domain_id))
        self.conn.commit()

    def add_comments(self, hostid, comments, overwrite=False):
        '''
        Add/append comments to object (currently used to add PO# data)
        overwrite optional // NOT IMPLEMENTED YET
        '''
        # get current comments
        sql = "select comment from RackObject where id=%s" % hostid
        result = self.sql_query(sql)
        try:
            comment = result[0]['comment']
        except IndexError:
            comment = ""

        # update / append to comments
        if comment:
            appended_comment = comment + '\n' + comments
            new_sql = "update RackObject set comment='%s' where id=%s" % (appended_comment, hostid)
        else:
            new_sql = "update RackObject set comment='%s' where id=%s" % (comments, hostid)
        self.cursor.execute(new_sql)
        self.conn.commit()


    def parse_args(self, hostid, args):
        '''
        function to process args if available
        '''
        keys = args.keys()
        if 'status' in keys:
            self.set_host_status(hostid, args['status'])
        if 'serial_no' in keys:
            self.set_host_serial_num(hostid, args['serial_no'])
        if 'domain' in keys:
            self.set_host_domain(hostid, args['domain'])
        if 'comment' in keys:
            self.add_comments(hostid, args['comment'])
        if 'tags' in keys:
            pass
        if 'hw_type' in keys:
            pass
        if 'contact' in keys:
            pass
        if 'os' in keys:
            pass
        if 'datacenter' in keys:
            pass
        if 'cabinet' in keys:
            pass
        if 'rack_loc' in keys:
            pass

    def put(self, hostname, data):
        '''
        update a host
        '''
        hostid = self.get_id(hostname)
        if hostid == None:
         abort(410)
        #args = request.form
        self.parse_args(hostid, data)
        newhost = self.get(hostname)
        return newhost

    def post(self, hostname, data):
        hostid = self.get_id(hostname)
        self.add_object(hostname)
        newhostid = self.get_id(hostname)
        self.parse_args(newhostid, data)
        newhost = self.get(hostname)
        return newhost

    def delete(self, hostname):
        '''
        delete a host by
        '''
        hostid = self.get_id(hostname)
        if hostid == None:
            abort(410)
        else:
            sql = ["delete from Object where id='%s'" % hostid,
                   "delete from TagStorage where entity_id='%s'" % hostid,
                   "delete from ObjectLog where object_id='%s'" % hostid,
                   "delete from ObjectHistory where id='%s'" % hostid]
            for q in sql:
                self.cursor.execute(q)
            self.conn.commit()
            result = {'data': [{'result': True}]}
            return result

    def get_comments(self, hostname):
        '''
        get host comments
        '''
        hostid = self.get_id(hostname)
        sql = "select comment from RackObject where id=%s" % hostid
        result = self.sql_query(sql)
        return result[0]