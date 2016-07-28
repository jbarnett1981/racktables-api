jbarnett
7/18/2016

To Do:
1. optional specify object type id in query
2. close connections properly if needed? (self.conn.close())
3. error handling
4. if bad data in request (HTTP 400), don't partially create host during POST / maybe some pre-check validation?
5. move credentials out of Dbconnect class

Fixed:
check if host exists before hitting /hosts/<hostname> and error appropriately
Fix querying old/invalid host/id error
Fix deleting old/invalid host/id error
Add check to set_host_serial_num to verify for existence of serial_num
Add to comment functionality
Removed reqparse - slated for deprecation. Using request.form instead.