import xlsxwriter
from random import seed
from random import randint

workbook = xlsxwriter.Workbook('new_2020_2.xlsx')
worksheet = workbook.add_worksheet("HPC")
worksheet.write(0, 0, "X")
worksheet.write(0, 1, "Y")
row = 1
col = 0

seed(randint(0, 10))
n = 500
limit1 = 800
limit2 = 1100
limit3 = 0
limit4 = 300
limit5 = 2500
limit6 = 2800
limit7 = 1700
limit8 = 2000

for i in range(n):
    x = randint(limit1,limit2)
    y = randint(limit1, limit2)
    worksheet.write(row, col, x)
    worksheet.write(row, col + 1, y)
    row += 1
    # x = randint(limit3, limit4)
    # y = randint(limit3, limit4)
    # worksheet.write(row, col, x)
    # worksheet.write(row, col + 1, y)
    # row += 1
    # x = randint(limit5, limit6)
    y = randint(limit5, limit6)
    worksheet.write(row, col, x)
    worksheet.write(row, col + 1, y)
    row += 1
    # x = randint(limit7, limit8)
    # y = randint(limit7, limit8)
    # worksheet.write(row, col, x)
    # worksheet.write(row, col + 1, y)
    # row += 1

workbook.close()