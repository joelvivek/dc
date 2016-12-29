import xlrd
import MySQLdb

book = xlrd.open_workbook("Book1.xlsx")
sheet = book.sheet_by_name("Sheet1")

# Establish a MySQL connection
database = MySQLdb.connect (host="localhost", user = "root", passwd = "root", db = "student")

# Get the cursor, which is used to traverse the database, line by line
cursor = database.cursor()

# Create the INSERT INTO sql query
query = """INSERT INTO student (id,sname,city) VALUES (%s, %s, %s)"""

# Create a For loop to iterate through each row in the XLS file, starting at row 2 to skip the headers
for r in range(1, sheet.nrows):
      sid      = sheet.cell(r,0).value
      sname = sheet.cell(r,1).value
      city     = sheet.cell(r,2).value

      # Assign values from each row
      values = (sid,sname,city)

      # Execute sql Query
      cursor.execute(query, values)

# Close the cursor
cursor.close()

# Commit the transaction
database.commit()

# Close the database connection
database.close()

# Print results
print ""
print "All Done! Bye, for now."
print ""
columns = str(sheet.ncols)
rows = str(sheet.nrows)
print "Insert done to DB"
