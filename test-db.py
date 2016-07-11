import pymysql

conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='renzhe123', db='mysql')
cur = conn.cursor()
cur.execute("USE sjd2016")
cur.execute("INSERT INTO users VALUES(1, 'www'),(2, 'cnblogs'),(3, 'com'),(4, 'txw1958')")
cur.execute("SELECT * FROM users")
for row in cur.fetchall():
    print('%s\t%s' % row)

cur.close()
conn.commit()
conn.close()