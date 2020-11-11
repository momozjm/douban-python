import xlwt

workbook = xlwt.Workbook(encoding="utf-8")  # 创建workbook对象
worksheet = workbook.add_sheet('sheet1')  # 创建工作表
worksheet.write(0, 0, 'hello')  # 行，列，数据
workbook.save('student.xls')  # 保存数据表
