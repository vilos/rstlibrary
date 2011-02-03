v1
/usr/local/bin/uwsgi -s /tmp/cherokee-uwsgi-vslibrary.sock -H /usr/local/var/www/vslib/ve/vslib  -x /usr/local/var/www/vslib/ve/vslib/src/vslibrary/uwsgi.conf -M -p 2

v2
/usr/bin/uwsgi -s /tmp/cherokee-uwsgi-library.sock -H /usr/local/var/www/vslib/ve/vslib  -w load_uwsgi -M -p 2
+
--logto /usr/local/var/www/vslib/ve/vslib/src/vslibrary/uwsgi.log
