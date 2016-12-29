import MySQLdb
import os
import sys
import json
import xlrd

data = xlrd.open_workbook("/tmp/idciris-new-user-request-form.xlsx")
sheet = data.sheet_by_name("Request")
db = MySQLdb.connect('10.137.2.81','test','test123','cmdb')
global values1
cursor = db.cursor()

# Create a For loop to iterate through each row in the XLS file, starting at row 2 to skip the headers
for r in range(1, sheet.nrows):
        username      = sheet.cell(r,0).value
        rolename = sheet.cell(r,1).value
        team     = sheet.cell(r,2).value

        values = (username,team)
        query2 = "SELECT user_id FROM login_user WHERE username = '"+username+"'"
        query3 = "SELECT role_id FROM t_role WHERE role_name = '"+rolename+"'"

        cursor.execute(query2)
        if cursor.rowcount > 0:
                for r in cursor.fetchall():
                        result = r[0]
                        print "result---->",result
        cursor.execute(query3)
        if cursor.rowcount > 0:
                for t in cursor.fetchall():
                        result1 = t[0]
                        print "result---->",result1
        values1 = (result,result1)

        if cursor.execute("SELECT username FROM login_user WHERE username = '"+username+"'") > 0:
                print "Already this user have the IDC Iris portal access"
                cursor.execute("UPDATE t_user_role SET role_id = '"+result1+"' WHERE user_id = '"+result+"'")
        else:
                query1 = """INSERT INTO login_user (username,team) VALUES (%s, %s)"""
                cursor.execute(query1,values)
                query4 = """INSERT INTO t_user_role (user_id,role_id) values (%s, %s)"""
                print "success",cursor.execute(query4,values1)

cursor.close()

db.commit()

db.close()

print "All Done! Bye, for now."
columns = str(sheet.ncols)
rows = str(sheet.nrows)
print "Insert done to DB"
