'''
jbarnett
7/18/2016

To Do:
1. optional specify object type id in query
2. close connections properly if needed? (self.conn.close())
3. error handling
4. if bad data in request (HTTP 400), don't partially create host during POST / maybe some pre-check validation?
5. move credentials out of DbConnect class

Fixed:
check if host exists before hitting /hosts/<hostname> and error appropriately
Fix querying old/invalid host/id error
Fix deleting old/invalid host/id error
Add check to set_host_serial_num to verify for existence of serial_num
Add to comment functionality
Removed reqparse - slated for deprecation. Using request.form instead.
'''

from flask import Flask, request, make_response, jsonify, abort
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from flask_httpauth import HTTPBasicAuth
import json
from error_handling import *

app = Flask(__name__)
api = Api(app, catch_all_404s=True, errors=errors)
auth = HTTPBasicAuth()

@auth.get_password
def get_password(username):
    if username == 'miguel':
        return 'python'
    return None

@auth.error_handler
def unauthorized():
    # return 403 instead of 401 to prevent browsers from displaying the default
    # auth dialog
    return make_response(jsonify({'message': 'Unauthorized access'}), 403)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

class Dbconnect:
    def __init__(self):
        '''
        init
        '''
        rtables_host = 'racktables.dev.tsi.lan'
        rtables_db = 'racktables_db'
        rtables_db_user = 'admin'
        rtables_db_pass = 'sZ#.f,8K$n'
        self.uri = 'mysql://%s:%s@%s/%s' % (rtables_db_user,rtables_db_pass, rtables_host, rtables_db)
        self.conn = None

    def _connect(self):
        '''
        Connect to Racktables DB
        '''
        if not self.conn:
            e = create_engine(self.uri)
            self.conn = e.connect()

    def sql_query(self, sql):
        '''
        sql query wrapper
        '''
        #Perform query and return JSON data
        self._connect()
        if type(sql) == list:
            for q in sql:
                result = self.conn.execute(q)
        else:
            result = self.conn.execute(sql)
        sqldict = [dict(zip(tuple (result.keys()) ,i)) for i in result]
        return sqldict

class Hosts(Dbconnect, Resource):
    def get(self):
        sql = "select * from Object"
        result = self.sql_query(sql)
        return jsonify({'hosts': [i['name'] for i in result]})

class Host(Dbconnect, Resource):

    def add_object(self, name, objtype_id=4):
        '''
        Create object
        '''
        self._connect()
        sql = "insert into Object (id, name, label, objtype_id, asset_no, has_problems, comment) values (NULL,'%s',NULL,%s,NULL,'no',NULL)" % (name, objtype_id)
        self.conn.execute(sql)

    def get(self, hostname):
        '''
        Get host info
        '''
        hostid = self.get_id(hostname)
        if hostid == None:
            raise ResourceDoesNotExist
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
        out = jsonify(result)
        # out.status_code = 200
        return out

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
        # query = self.conn.execute("select distinct id,name, dict_value hw_type from Object t1 left join AttributeValue t2 on t1.id=t2.object_id left join TagStorage t3 on t1.id=t3.entity_id left join Dictionary t4 on t2.uint_value=t4.dict_key where t2.attr_id=2 and t1.id='%s'" % hostname)
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
        self._connect()
        status_id = self.get_status_id(statusname)
        if status_id == None:
            raise ResourceDoesNotExist
        # Get status: if None insert record, otherwise update existing
        try:
            status_exists = self.get_host_status(hostid)
        except TypeError:
            pass
        if status_exists == None:
            self.conn.execute("insert into AttributeValue (object_id, object_tid, attr_id, string_value, uint_value, float_value) values (%s,4,10005,NULL,%s,NULL) on duplicate key update object_id=object_id""", (hostid, status_id))
        else:
            self.conn.execute("update AttributeValue set uint_value=%s where attr_id=10005 and object_id=%s""", (status_id, hostid))

    def set_host_serial_num(self, hostid, serial_num):
        '''
        Update the serial number of a given host id. raise ResourceAlreadyExists if serial_no already exists.
        '''
        serial_exists = self.get_serial_num_exist(serial_num)
        if serial_exists:
            raise ResourceAlreadyExists
        try:
            serial_exists = self.get_host_serial_num(hostid)
        except TypeError:
            serial_exists = None
        if serial_exists == None:
            self.conn.execute("insert into AttributeValue (object_id, object_tid, attr_id, string_value, uint_value, float_value) values (%s,4,1,%s,NULL,NULL) on duplicate key update object_id=object_id", (hostid, serial_num))
        else:
            self.conn.execute("update AttributeValue set string_value=%s where attr_id=1 and object_id=%s", (serial_num, hostid))

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
            raise BadRequest
        try:
            domain_already_configured = self.get_host_domain(hostid)
        except TypeError:
            domain_already_configured = None
        if domain_already_configured:
            self.conn.execute("update AttributeValue set uint_value=%s where attr_id=10002 and object_id=%s", (domain_id, hostid))
        else:
            self.conn.execute("insert into AttributeValue (object_id, object_tid, attr_id, string_value, uint_value, float_value) values (%s,4,10002,NULL,%s,NULL) on duplicate key update object_id=object_id", (hostid, domain_id))

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
        self.conn.execute(new_sql)


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

    def put(self, hostname):
        '''
        update a host
        '''
        hostid = self.get_id(hostname)
        if hostid == None:
         raise ResourceDoesNotExist
        args = request.form
        self.parse_args(hostid, args)
        newhost = self.get(hostname)
        return newhost

    def post(self, hostname):
        hostid = self.get_id(hostname)
        if hostid != None:
            raise ResourceAlreadyExists
        self.add_object(hostname)
        newhostid = self.get_id(hostname)
        args = request.form
        self.parse_args(newhostid, args)
        newhost = self.get(hostname)
        return newhost

    def delete(self, hostname):
        '''
        delete a host by
        '''
        self._connect()
        hostid = self.get_id(hostname)
        if hostid == None:
            raise ResourceDoesNotExist
        else:
            sql = ["delete from Object where id='%s'" % hostid,
                   "delete from TagStorage where entity_id='%s'" % hostid,
                   "delete from ObjectLog where object_id='%s'" % hostid,
                   "delete from ObjectHistory where id='%s'" % hostid]
            for q in sql:
                self.conn.execute(q)
            result = {'data': [{'result': True}]}
            return jsonify(result)

class Comments(Host):
    def get(self, hostname):
        hostid = self.get_id(hostname)
        sql = "select comment from RackObject where id=%s" % hostid
        result = self.sql_query(sql)
        return jsonify(result[0])

api.add_resource(Hosts, '/hosts')
api.add_resource(Host, '/hosts/<string:hostname>')
api.add_resource(Comments, '/hosts/<string:hostname>/comments')

if __name__ == '__main__':
    # app.run(host='0.0.0.0', debug=True)
    app.run(debug=True)