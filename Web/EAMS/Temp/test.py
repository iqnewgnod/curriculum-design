from flask import Flask, render_template, request, url_for, redirect, session, flash, send_from_directory, jsonify
from db import useSQLite
import os
import xlwt
import xlrd
from werkzeug.utils import secure_filename
from datetime import timedelta

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
UPLOAD_FOLDER = 'upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # 设置文件上传的目标文件夹
basedir = os.path.abspath(os.path.dirname(__file__))  # 获取当前项目的绝对路径


# @app.route('/')
# def index():
#     session['stuid'] = '201701001'
#     session['staid'] = '0001'
#     session['teaid'] = '0001'
#     session['exist'] = '1'
#     return render_template("login.html")


@app.route('/login', methods=["POST", "GET"])
def login():
    #
    if request.method == "POST":
        id = request.form['id']
        pw = request.form['pw']
        ty = request.form['ty']
        if ty == "student":
            sql = "select 密码 from student where 学号='%s' and 密码='%s'" % (id, pw)
            res = useSQLite.query(sql)
            if len(res) == 0:
                flash("账号或密码错误！")
                return render_template("logintemp.html")
            else:
                session['exist'] = '1'
                session['stuid'] = id
                return redirect(url_for('student'))
        elif ty == "teacher":
            sql = "select 密码 from teacher where 编号='%s' and 密码='%s'" % (id, pw)
            res = useSQLite.query(sql)
            if len(res) == 0:
                flash("账号或密码错误！")
                return render_template("logintemp.html")
            else:
                session['exist'] = '1'
                session['teaid'] = id
                return redirect(url_for('teacher'))
        elif ty == "staff":
            sql = "select 密码 from staff where 教工号='%s' and 密码='%s'" % (id, pw)
            res = useSQLite.query(sql)
            if len(res) == 0:
                flash("账号或密码错误！")
                return render_template("logintemp.html")
            else:
                session['exist'] = '1'
                session['staff'] = id
                return redirect(url_for('staff'))
    else:
        return render_template("logintemp.html")


@app.route('/student', methods=["GET", "POST"])
def student():
    if session.get('exist') == None:
        flash("请登录！")
        return redirect(url_for('login'))
    return render_template("student/student.html")


@app.route('/student/queryInf')
def stu_queryInf():
    if session.get('exist') == None:
        flash("请登录！")
        return redirect(url_for('login'))
    return render_template("student/queryInf/queryInf.html")


@app.route('/student/queryInf/query')
def stu_queryInf_query():
    if session.get('exist') == None:
        flash("请登录！")
        return redirect(url_for('login'))
    stuid = session.get("stuid")
    res = useSQLite.query("select * from student where 学号='%s'" % stuid)
    return render_template("student/queryInf/query.html", res=res)


@app.route('/student/queryInf/changePwd', methods=["POST", "GET"])
def stu_queryInf_changePwd():
    if session.get('exist') == None:
        flash("请登录！")
        return redirect(url_for('login'))

    if request.method == "GET":
        return render_template("student/queryInf/changePwd.html")
    stuid = session.get("stuid")
    res = useSQLite.query("select 密码 from student where 学号='%s'" % stuid)
    old = request.form['old']
    if res[0][0] != old:
        flash("原密码错误，请重新输入！")
        return render_template("student/queryInf/changePwd.html")
    try:
        new = request.form['new']
        sql = "update student set 密码 = '%s' where 学号 = '%s'" % (new, stuid)
        useSQLite.insertOrDeleteOrUpdate(sql)
        flash("修改成功！")
        return render_template("student/queryInf/changePwd.html")
    except:
        flash("密码内容有误，请重新输入！")
        return render_template("student/queryInf/changePwd.html")


@app.route('/student/course')
def stu_courseSel():
    if session.get('exist') == None:
        flash("请登录！")
        return redirect(url_for('login'))
    return render_template("student/course/course.html")


@app.route('/student/course/select', methods=["GET"])
def stu_courseSel_select():
    if session.get('exist') == None:
        flash("请登录！")
        return redirect(url_for('login'))
    if request.method == "GET":
        return render_template("student/course/select.html", res=None, head=None, res2=None)
    # else:
    #     stuid = session.get('stuid')
    #     stucls = useSQLite.query("select 班级 from student where 学号='%s'" % stuid)[0][0]
    #     res = useSQLite.query(
    #         "select 课程名, 课程编号, 任课教师, 开课班级, 选课人数上限, 开课学期, 剩余人数, 课序号 from selectCourse where 开课班级 = '%s' and 课序号 not in (select 课序号 from studentCourse where 学号='%s')" % (
    #             stucls, stuid))
    #     head = useSQLite.query_head_diy("select  课程名, 课程编号, 任课教师, 开课班级, 选课人数上限, 开课学期, 剩余人数, 课序号 from selectCourse")
    #     res2 = useSQLite.query(
    #         "select 课程名, 课程编号, 任课教师, 开课班级, 选课人数上限, 开课学期, 剩余人数, 课序号 from selectCourse where 开课班级 = '%s' and 课序号 in (select 课序号 from studentCourse where 学号='%s')" % (
    #             stucls, stuid))
    #     return render_template("student/course/select.html", res=res, head=head, res2=res2)


@app.route('/student/course/select3', methods=["POST", "GET"])
def stu_courseSel_select3():
    if session.get('exist') == None:
        flash("请登录！")
        return redirect(url_for('login'))
    if request.method == "GET":
        stuid = session.get('stuid')
        stucls = useSQLite.query("select 班级 from student where 学号='%s'" % stuid)[0][0]
        res = useSQLite.query(
            "select 课程名, 课程编号, 任课教师, 开课班级, 选课人数上限, 开课学期, 剩余人数, 课序号 from selectCourse where 开课班级 = '%s' and 课序号 not in (select 课序号 from studentCourse where 学号='%s')" % (
                stucls, stuid))
        head = useSQLite.query_head_diy("select  课程名, 课程编号, 任课教师, 开课班级, 选课人数上限, 开课学期, 剩余人数, 课序号 from selectCourse")
        res2 = useSQLite.query(
            "select 课程名, 课程编号, 任课教师, 开课班级, 选课人数上限, 开课学期, 剩余人数, 课序号 from selectCourse where 开课班级 = '%s' and 课序号 in (select 课序号 from studentCourse where 学号='%s')" % (
                stucls, stuid))
        return render_template("student/course/select.html", res=res, head=head, res2=res2)
    else:
        cbox = request.form.getlist("cbox")
        cbox = list(cbox)
        stuid = session.get('stuid')
        cannot = []
        can = []
        for i in cbox:
            sql = "insert into studentCourse values('%s', '%s', 0)" % (stuid, i)
            sql_last = "select 剩余人数 from selectCourse where 课序号='%s'" % i
            leftnum = int(useSQLite.query(sql_last)[0][0])
            num = leftnum - 1
            if leftnum == 0:
                cannot.append(i)
                continue
            useSQLite.insertOrDeleteOrUpdate(sql)
            up = "update selectCourse set 剩余人数 = %d where 课序号 = '%s'" % (num, i)
            useSQLite.insertOrDeleteOrUpdate(up)
            can.append(i)
        return redirect(url_for('stu_courseSel_select3'))


#
# @app.route('/student/course/select2', methods=["POST"])
# def stu_courseSel_select2():
#     if request.method == "POST":
#         cbox = request.form.getlist("cbox")
#         cbox = list(cbox)
#         stuid = session.get('stuid')
#         cannot = []
#         can = []
#         for i in cbox:
#             sql = "insert into studentCourse values('%s', '%s', 0)" % (stuid, i)
#             # try:
#             sql_last = "select 剩余人数 from selectCourse where 课序号='%s'" % i
#             leftnum = int(useSQLite.query(sql_last)[0][0])
#             num = leftnum - 1
#             if leftnum == 0:
#                 cannot.append(i)
#                 continue
#             useSQLite.insertOrDeleteOrUpdate(sql)
#             up = "update selectCourse set 剩余人数 = %d where 课序号 = '%s'" % (num, i)
#             useSQLite.insertOrDeleteOrUpdate(up)
#             can.append(i)
#             # except:
#             #     flash("选课出错，请重新选择！")
#             #     return redirect(url_for('stu_courseSel_select'))
#         s = "课程："
#         for i in range(0, len(can)):
#             s += can[i] + " "
#         s += " 选修成功"
#         s2 = "课程："
#         for i in range(0, len(cannot)):
#             s2 += cannot[i] + " "
#         s2 += " 选修失败"
#         if len(can) != 0:
#             flash(s)
#         if len(cannot) != 0:
#             flash(s2)
#         return redirect(url_for('stu_courseSel_select'))

@app.route('/student/course/delete', methods=["GET"])
def stu_courseSel_delete():
    if session.get('exist') == None:
        flash("请登录！")
        return redirect(url_for('login'))
    if request.method == "GET":
        return render_template("student/course/delete.html", res=None, head=None, res2=None)
    # else:
    #     stuid = session.get('stuid')
    #     stucls = useSQLite.query("select 班级 from student where 学号='%s'" % stuid)[0][0]
    #     head = useSQLite.query_head_diy("select  课程名, 课程编号, 任课教师, 开课班级, 选课人数上限, 开课学期, 剩余人数, 课序号 from selectCourse")
    #     res = useSQLite.query(
    #         "select 课程名, 课程编号, 任课教师, 开课班级, 选课人数上限, 开课学期, 剩余人数, 课序号 from selectCourse where 开课班级 = '%s' and 课序号 in (select 课序号 from studentCourse where 学号='%s')" % (
    #             stucls, stuid))
    #     return render_template("student/course/delete.html", res=res, head=head, res2=res)


@app.route('/student/course/delete3', methods=["POST", "GET"])
def stu_courseSel_delete3():
    if session.get('exist') == None:
        flash("请登录！")
        return redirect(url_for('login'))
    if request.method == "GET":
        stuid = session.get('stuid')
        stucls = useSQLite.query("select 班级 from student where 学号='%s'" % stuid)[0][0]
        head = useSQLite.query_head_diy("select  课程名, 课程编号, 任课教师, 开课班级, 选课人数上限, 开课学期, 剩余人数, 课序号 from selectCourse")
        res = useSQLite.query(
            "select 课程名, 课程编号, 任课教师, 开课班级, 选课人数上限, 开课学期, 剩余人数, 课序号 from selectCourse where 开课班级 = '%s' and 课序号 in (select 课序号 from studentCourse where 学号='%s')" % (
                stucls, stuid))
        return render_template("student/course/delete.html", res=res, head=head, res2=res)
    else:
        cbox = request.form.getlist("cbox")
        cbox = list(cbox)
        stuid = session.get('stuid')
        can = []
        for i in cbox:
            sql = "delete from studentCourse where 学号='%s' and 课序号='%s'" % (stuid, i)
            sql_last = "select 剩余人数 from selectCourse where 课序号='%s'" % i
            leftnum = int(useSQLite.query(sql_last)[0][0])
            num = leftnum + 1
            useSQLite.insertOrDeleteOrUpdate(sql)
            up = "update selectCourse set 剩余人数 = %d where 课序号 = '%s'" % (num, i)
            useSQLite.insertOrDeleteOrUpdate(up)
            can.append(i)
        return redirect(url_for('stu_courseSel_delete3'))


# @app.route('/student/course/delete2', methods=["POST"])
# def stu_courseSel_delete2():
#     if request.method == "POST":
#         cbox = request.form.getlist("cbox")
#         cbox = list(cbox)
#         stuid = session.get('stuid')
#         can = []
#         for i in cbox:
#             sql = "delete from studentCourse where 学号='%s' and 课序号='%s'" % (stuid, i)
#             sql_last = "select 剩余人数 from selectCourse where 课序号='%s'" % i
#             leftnum = int(useSQLite.query(sql_last)[0][0])
#             num = leftnum + 1
#             useSQLite.insertOrDeleteOrUpdate(sql)
#             up = "update selectCourse set 剩余人数 = %d where 课序号 = '%s'" % (num, i)
#             useSQLite.insertOrDeleteOrUpdate(up)
#             can.append(i)
#         s = "课程："
#         for i in range(0, len(can)):
#             s += can[i] + " "
#         s += " 退课成功"
#         if len(can) != 0:
#             flash(s)
#         return redirect(url_for('stu_courseSel_delete'))


@app.route('/student/grade/query', methods=["POST", "GET"])
def stu_grade_query():
    if session.get('exist') == None:
        flash("请登录！")
        return redirect(url_for('login'))
    if request.method == "GET":
        return render_template("student/grade/query.html", res=None, head=None)
    else:
        stuid = session.get('stuid')
        sql = "select 课程名, 课程编号, 任课教师,开课班级 , 成绩 from selectCourse a, studentCourse b where a. 课序号=b.课序号 and b.学号='%s'" % stuid
        res = useSQLite.query(sql)
        head = useSQLite.query_head_diy(
            "select 课程名, 课程编号, 任课教师,开课班级 , 成绩 from selectCourse a, studentCourse b where a. 课序号=b.课序号")
        return render_template("student/grade/query.html", res=res, head=head)


@app.route('/student/changePwd')
def stu_changPwd():
    if session.get('exist') == None:
        flash("请登录！")
        return redirect(url_for('login'))
    return render_template("student/changePwd.html")


@app.route('/loginTea', methods=['POST'])
def loginTea():
    if session.get('exist') == None:
        flash("请登录！")
        return redirect(url_for('login'))
    return redirect(url_for('teacher'))


@app.route('/teacher', methods=["GET", "POST"])
def teacher():
    if session.get('exist') == None:
        flash("请登录！")
        return redirect(url_for('login'))
    return render_template("teacher/teacher.html")


@app.route('/teacher/course')
def tea_changPwd():
    if session.get('exist') == None:
        flash("请登录！")
        return redirect(url_for('login'))
    return render_template("teacher/changePwd/changePwd.html")


@app.route('/teacher/course/query', methods=["POST", "GET"])
def tea_changPwd_query():
    if session.get('exist') == None:
        flash("请登录！")
        return redirect(url_for('login'))
    if request.method == "GET":
        return render_template("teacher/course/query.html", res=None, head=None)
    else:
        teaid = session.get('teaid')
        sql = "select 课序号, 课程名,课程编号,任课教师, 开课年份, 开课班级, 选课人数上限, 开课学期, 剩余人数 from selectCourse where 任课老师编号='%s'" % teaid
        res = useSQLite.query(sql)
        head = useSQLite.query_head_diy("select 课序号, 课程名,课程编号,任课教师, 开课年份, 开课班级, 选课人数上限, 开课学期, 剩余人数 from selectCourse")
        if len(res) == 0:
            flash("为查到任何开课信息！")
            return render_template("teacher/course/query.html", res=None, head=None)
        return render_template("teacher/course/query.html", res=res, head=head)


@app.route('/teacher/course/student', methods=["GET"])
def tea_course_student():
    if session.get('exist') == None:
        flash("请登录！")
        return redirect(url_for('login'))
    if request.method == "GET":
        return render_template("teacher/course/student.html", res=None, head=None, dirpath=None)
    # else:
    #     teaid = session.get('teaid')
    #     va = request.form['txt']
    #     sql = "select a.课序号, 课程名, 开课班级,姓名, b.学号, 成绩  from selectCourse a, studentCourse b, student c where a.课序号='%s' and a.课序号= b.课序号 and b.学号=c.学号 and 任课老师编号='%s'" % (
    #         va, teaid)
    #     res = useSQLite.query(sql)
    #     if len(res) == 0:
    #         flash("未查询到任何信息！")
    #         return render_template("teacher/course/student.html", res=None, head=None, dirpath=None)
    #     head = useSQLite.query_head_diy(
    #         "select a.课序号, 课程名, 开课班级,姓名, b.学号, 成绩  from selectCourse a, studentCourse b, student c where a.课序号= b.课序号 and b.学号=c.学号")
    #
    #     # 生成EXCEL
    #     workbook = xlwt.Workbook(encoding='utf-8')
    #     worksheet = workbook.add_sheet(head[1])
    #     for i in range(0, len(head)):
    #         worksheet.write(0, i, label=head[i])
    #
    #     for i in range(1, len(res) + 1):
    #         for j in range(0, len(res[i - 1])):
    #             worksheet.write(i, j, label=res[i - 1][j])
    #
    #     dirpath = os.path.join(os.path.dirname(__file__), 'upload', str(res[0][0] + '.xls'))
    #     workbook.save(dirpath)
    #     path = res[0][0] + ".xls"
    #
    #     return render_template("teacher/course/student.html", res=res, head=head, dirpath=path)


@app.route('/teacher/course/student3', methods=["POST", "GET"])
def tea_course_student3():
    if session.get('exist') == None:
        flash("请登录！")
        return redirect(url_for('login'))
    if request.method == "GET":
        teaid = session.get('teaid')
        va = request.args['txt']
        sql = "select a.课序号, 课程名, 开课班级,姓名, b.学号, 成绩  from selectCourse a, studentCourse b, student c where a.课序号='%s' and a.课序号= b.课序号 and b.学号=c.学号 and 任课老师编号='%s'" % (
            va, teaid)
        res = useSQLite.query(sql)
        if len(res) == 0:
            flash("未查询到任何信息！")
            return render_template("teacher/course/student.html", res=None, head=None, dirpath=None)
        head = useSQLite.query_head_diy(
            "select a.课序号, 课程名, 开课班级,姓名, b.学号, 成绩  from selectCourse a, studentCourse b, student c where a.课序号= b.课序号 and b.学号=c.学号")

        # 生成EXCEL
        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet(head[1])
        for i in range(0, len(head)):
            worksheet.write(0, i, label=head[i])

        for i in range(1, len(res) + 1):
            for j in range(0, len(res[i - 1])):
                worksheet.write(i, j, label=res[i - 1][j])

        dirpath = os.path.join(os.path.dirname(__file__), 'upload', str(res[0][0] + '.xls'))
        workbook.save(dirpath)
        path = res[0][0] + ".xls"
        return render_template("teacher/course/student.html", res=res, head=head, dirpath=path)
    else:
        txt = request.form['txt']
        couid = request.form.getlist("hid_couid")
        stuid = request.form.getlist("hid_stuid")
        grade = request.form.getlist("grade")
        try:
            for i in range(0, len(couid)):
                up = "update studentCourse set 成绩='%s' where 学号='%s' and 课序号='%s'" % (grade[i], stuid[i], couid[i])
                useSQLite.insertOrDeleteOrUpdate(up)
            flash("成绩修改成功！")
            return redirect("/teacher/course/student3" + "?txt=" + txt)
        except:
            flash("成功录入出错！")
            return redirect("/teacher/course/student3" + "?txt=" + txt)


@app.route('/excel', methods=["get"])
def excel():
    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet('My Worksheet')
    worksheet.write(1, 0, label='this is testssss')
    workbook.save('D:\\1.xls')
    return "ok"


@app.route("/download/<path:filename>")
def downloader(filename):
    dirpath = os.path.join(app.root_path, 'upload')  # 这里是下在目录，从工程的根目录写起，比如你要下载static/js里面的js文件，这里就要写“static/js”
    return send_from_directory(dirpath, filename, as_attachment=True)  # as_attachment=True 一定要写，不然会变成打开，而不是下载


@app.route("/test", methods=["POST", "GET"])
def test():
    file = request.files['file']  # 获取文件
    filename = file.filename
    upload_path = os.path.join(os.path.dirname(__file__), 'upload', filename)
    file.save(upload_path)
    workbook = xlrd.open_workbook(upload_path)
    table = workbook.sheets()[0]
    row = table.nrows
    col = table.ncols
    for i in range(1, row):
        for j in range(0, col):
            print(table.cell(i, j).value)
    return "OK"


@app.route("/upload", methods=["POST", "GET"])
def uptest():
    if request.method == "GET":
        return render_template("filetest.html")
    else:
        file = request.files['file']  # 获取文件
        filename = file.filename
        upload_path = os.path.join(os.path.dirname(__file__), 'upload', filename)
        file.save(upload_path)

        return filename


# @app.route('/teacher/course/student2', methods=["POST"])
# def tea_course_student2():
#     if request.method == "POST":
#         couid = request.form.getlist("hid_couid")
#         stuid = request.form.getlist("hid_stuid")
#         grade = request.form.getlist("grade")
#         try:
#             for i in range(0, len(couid)):
#                 up = "update studentCourse set 成绩='%s' where 学号='%s' and 课序号='%s'" % (grade[i], stuid[i], couid[i])
#                 useSQLite.insertOrDeleteOrUpdate(up)
#             flash("成绩修改成功！")
#             return render_template("teacher/course/student.html", res=None, head=None)
#         except:
#             flash("成功录入出错！")
#             return render_template("teacher/course/student.html", res=None, head=None)


@app.route('/teacher/queryInfo')
def tea_queryInfo():
    if session.get('exist') == None:
        flash("请登录！")
        return redirect(url_for('login'))
    return render_template("teacher/queryInfo.html")


@app.route('/teacher/inputGra')
def tea_inputGra():
    if session.get('exist') == None:
        flash("请登录！")
        return redirect(url_for('login'))
    return render_template("teacher/inputGra.html")


@app.route('/loginSta', methods=['POST'])
def loginSta():
    if session.get('exist') == None:
        flash("请登录！")
        return redirect(url_for('login'))
    return redirect(url_for('staff'))


@app.route('/staff')
def staff():
    if session.get('exist') == None:
        flash("请登录！")
        return redirect(url_for('login'))
    return render_template("staff/staff.html")


@app.route('/staff/changePwd', methods=["POST", "GET"])
def sta_changePwd():
    if session.get('exist') == None:
        flash("请登录！")
        return redirect(url_for('login'))
    if request.method == "GET":
        return render_template("staff/changePwd/changePwd.html")
    else:
        staid = session.get('staid')
        old = request.form['old']
        sql_exist = useSQLite.query("select * from staff where 教工号 = '%s'" % staid)[0][0]
        if old != sql_exist:
            flash("密码错误！")
            return render_template("staff/changePwd/changePwd.html")
        try:
            new = request.form['new']
            up = "update staff set 密码='%s' where 教工号= '%s'" % (new, staid)
            useSQLite.insertOrDeleteOrUpdate(up)
            flash("密码修改成功!")
            return render_template("staff/changePwd/changePwd.html")
        except:
            flash("密码修改失败!")
            return render_template("staff/changePwd/changePwd.html")


@app.route('/staff/changeStuInfo')
def sta_changeStuInfo():
    if session.get('exist') == None:
        flash("请登录！")
        return redirect(url_for('login'))
    return render_template("staff/changeStuInfo/changeStuInfo.html")


@app.route('/staff/changeStuInfo/query', methods=['GET', 'POST'])
def sta_changeStuInfo_query():
    if session.get('exist') == None:
        flash("请登录！")
        return redirect(url_for('login'))
    if request.method == 'GET':
        return render_template("staff/changeStuInfo/query.html", res=None, head=None, ty=None)
    else:
        # ty = request.form['sel']
        value = request.form['txt']
        sql = "select * from student where 学号 = '%s' and 删除 !='是' " % (value)
        # print(sql)
        # return  "OK"
        try:
            res = useSQLite.query(sql)
            if len(res) == 0:
                flash("未找到相关信息！")
                return render_template("staff/changeStuInfo/query.html", res=None, head=None)
            head = useSQLite.query_head('student')
            return render_template("staff/changeStuInfo/query.html", res=res, head=head)
        except:
            flash("未找到相关信息！")
            return render_template("staff/changeStuInfo/query.html", res=None, head=None)


@app.route('/staff/changeStuInfo/add', methods=['GET', 'POST'])
def sta_changeStuInfo_add():
    if session.get('exist') == None:
        flash("请登录！")
        return redirect(url_for('login'))
    if request.method == 'GET':
        sql_cls = "select * from class"
        cls = useSQLite.query(sql_cls)
        sql_maj = "select * from major"
        maj = useSQLite.query(sql_maj)
        return render_template("staff/changeStuInfo/add.html", cls=cls, maj=maj)
    else:
        # files = request.files.get('file')
        f = request.files['照片']
        sql_filename = "select count(*) from student order by 照片 DESC"
        f_name = int(useSQLite.query(sql_filename)[0][0]) + 1
        f_temp = str(f_name).rjust(3, '0')
        f_name = str(f_name).rjust(3, '0') + ".png"
        f.filename = f_name
        upload_path = os.path.join(os.path.dirname(__file__), 'static/picture/student', f.filename)
        f.save(upload_path)
        head = useSQLite.query_head('student')
        name = request.form['姓名']
        pw = request.form['密码']
        yyy = request.form['出生年份']
        mmm = request.form['出生月份']
        ddd = request.form['出生日份']
        sex = ""
        if request.form['性别'] == "男":
            sex = "男"
        else:
            sex = "女"
        cls = request.form['班级']
        maj = request.form['专业']
        cls_id = useSQLite.query("select 班级号 from class where 班级名='%s'" % cls)[0][0]
        cls_num = useSQLite.query("select count(*) from student where 班级 = '%s'" % cls)[0][0] + 1
        id = cls_id + str(cls_num).rjust(3, '0')
        sql = "insert into student values('%s','%s','%s','%s', %d, %d, %d, '%s', '%s', '%s','否')" % (
            id, name, maj, sex, int(yyy), int(mmm), int(ddd), cls, pw, f_temp)
        useSQLite.insertOrDeleteOrUpdate(sql)
        flash("添加成功")
        return redirect(url_for('sta_changeStuInfo_add'))


@app.route('/staff/changeStuInfo/delete', methods=["GET"])
def sta_changeStuInfo_delete():
    if session.get('exist') == None:
        flash("请登录！")
        return redirect(url_for('login'))
    return render_template("staff/changeStuInfo/delete.html", res=None, head=None)


@app.route('/staff/changeStuInfo/delete2', methods=["GET", "POST"])
def sta_changeStuInfo_delete2():
    if session.get('exist') == None:
        flash("请登录！")
        return redirect(url_for('login'))
    if request.method == "GET":
        ty = request.args['sel']
        value = request.args['txt']
        sql = "select * from student where %s = '%s' and 删除 !='是' " % (ty, value)
        print(sql)
        try:
            res = useSQLite.query(sql)
            if len(res) == 0:
                flash("未找到相关信息！")
                return render_template("staff/changeStuInfo/delete.html", res=None, head=None, ty=None, value=None)
            head = useSQLite.query_head('student')
            return render_template("staff/changeStuInfo/delete.html", res=res, head=head, ty=ty, value=value)
        except:
            flash("未找到相关信息！")
            return render_template("staff/changeStuInfo/delete.html", res=None, head=None, ty=None, value=None)
    else:
        ty = request.form['sel']
        value = request.form['txt']
        cbox = request.form.getlist("cbox")
        cbox = list(cbox)
        can = []
        try:
            for i in cbox:
                sql = "update student set 删除 = '是' where 学号 = '%s'" % i
                print(sql)
                useSQLite.insertOrDeleteOrUpdate(sql)
                can.append(i)
            if len(can) != 0:
                flash("删除成功！")
            return redirect("/staff/changeStuInfo/delete2?sel=" + ty + "&txt=" + value)
        except:
            flash("删除失败！")
            return redirect("/staff/changeStuInfo/delete2?sel=" + ty + "&txt=" + value)


@app.route('/staff/changeStuInfo/change', methods=["GET", "POST"])
def sta_changeStuInfo_change():
    if session.get('exist') == None:
        flash("请登录！")
        return redirect(url_for('login'))
    if request.method == "GET":
        return render_template("staff/changeStuInfo/change.html", res=None, cls=None, maj=None)
    else:
        id = request.form['id']
        sql = "select * from student where 学号 = '%s' and 删除 =='否'" % id
        try:
            res = useSQLite.query(sql)
            if len(res) == 0:
                flash("未查询到相关信息！")
                return render_template("staff/changeStuInfo/change.html", res=None, cls=None, maj=None)
            cls_all = useSQLite.query("select * from class")
            maj_all = useSQLite.query("select * from major")
            return render_template("staff/changeStuInfo/change.html", res=res, cls=cls_all, maj=maj_all)
        except:
            flash("未查询到相关信息！")
            return render_template("staff/changeStuInfo/change.html", res=None, cls=None, maj=None)


@app.route('/staff/changeStuInfo/change2', methods=["POST"])
def sta_changeStuInfo_change2():
    if session.get('exist') == None:
        flash("请登录！")
        return redirect(url_for('login'))
    if request.method == "POST":
        id = request.form['id']
        sql = "select 学号,姓名,专业,性别,出生年份,出生月份,出生日份,班级,密码 from student where 学号 = '%s' and 删除 =='否'" % id
        res = useSQLite.query(sql)[0]
        sql_Pic = "select 照片 from student where 学号 = '%s'" % id
        res_pic = useSQLite.query(sql_Pic)[0]
        f = request.files['file']
        f.filename = res_pic[0] + ".png"
        upload_path = os.path.join(os.path.dirname(__file__), 'static/picture/student', f.filename)
        f.save(upload_path)
        new = []
        new.append(id)
        new.append(request.form['name'])
        new.append(request.form['maj'])
        new.append(request.form['sex'])
        new.append(request.form['yyy'])
        new.append(request.form['mmm'])
        new.append(request.form['ddd'])
        new.append(request.form['cls'])
        new.append(request.form['pw'])
        head = useSQLite.query_head('student')
        head.pop(10)
        head.pop(9)
        for i in range(0, len(res)):
            if res[i] != new[i]:
                sql_up = "update student set %s = '%s' where 学号 = '%s'" % (head[i], new[i], id)
                useSQLite.insertOrDeleteOrUpdate(sql_up)
        flash("修改成功！")
        return redirect(url_for('sta_changeStuInfo_change'))


@app.route('/staff/changeCou')
def sta_changeCou():
    if session.get('exist') == None:
        flash("请登录！")
        return redirect(url_for('login'))
    return render_template("staff/changeCou/changeCou.html")


@app.route('/staff/changeCou/query', methods=["POST", "GET"])
def sta_changeCou_query():
    if session.get('exist') == None:
        flash("请登录！")
        return redirect(url_for('login'))
    if request.method == "GET":
        return render_template("staff/changeCou/query.html", res=None, head=None)
    else:
        sel_ty = request.form['sel']
        va = request.form['txt']
        sql = "select 课序号, 课程名,课程编号,任课教师, 开课年份, 开课班级, 选课人数上限, 开课学期, 剩余人数 from selectCourse where %s = '%s'" % (
            sel_ty, va)
        try:
            res = useSQLite.query(sql)
            if len(res) == 0:
                flash("未查询到相关信息！")
                return render_template("staff/changeCou/query.html", res=None, head=None)
            head = useSQLite.query_head_diy(
                'select 课序号, 课程名,课程编号, 任课教师, 开课年份,开课班级, 选课人数上限, 开课学期, 剩余人数 from selectCourse')
            return render_template('staff/changeCou/query.html', res=res, head=head)
        except:
            flash("未查询到相关信息！")
            return render_template("staff/changeCou/query.html", res=None, head=None)


@app.route('/staff/changeCou/query2', methods=["POST", "GET"])
def sta_changeCou_query2():
    if session.get('exist') == None:
        flash("请登录！")
        return redirect(url_for('login'))
    if request.method == "GET":
        sel_ty = request.args['sel']
        va = request.args['txt']
        sql = "select 课序号, 课程名,课程编号,任课教师, 开课年份, 开课班级, 选课人数上限, 开课学期, 剩余人数 from selectCourse where %s = '%s'" % (
            sel_ty, va)
        try:
            res = useSQLite.query(sql)
            if len(res) == 0:
                flash("未查询到相关信息！")
                return render_template("staff/changeCou/query.html", res=None, head=None, ty=None, va=None)
            head = useSQLite.query_head_diy(
                'select 课序号, 课程名,课程编号, 任课教师, 开课年份,开课班级, 选课人数上限, 开课学期, 剩余人数 from selectCourse')
            return render_template('staff/changeCou/query.html', res=res, head=head, ty=sel_ty, va=va)
        except:
            flash("未查询到相关信息！")
            return render_template("staff/changeCou/query.html", res=None, head=None, ty=None, va=None)
    else:
        cbox_id = request.form.getlist("cbox_id")
        cbox_id = list(cbox_id)
        cbox2_cls = request.form.getlist("cbox2_cls")
        cbox2_cls = list(cbox2_cls)
        sel_ty = request.form['sel']
        va = request.form['txt']
        try:
            for i in range(0, len(cbox_id)):
                sql = "delete from selectCourse where 课序号= '%s' and 开课班级='%s'" % (cbox_id[i], cbox2_cls[i])
                useSQLite.insertOrDeleteOrUpdate(sql)
            flash("删除成功")
            return redirect("/staff/changeCou/query2?sel=" + sel_ty + "&txt=" + va)
        except:
            flash("删除失败")
            return redirect("/staff/changeCou/query2?sel=" + sel_ty + "&txt=" + va)


@app.route('/staff/changeCou/delete', methods=["GET", "POST"])
def sta_changeCou_delete():
    if session.get('exist') == None:
        flash("请登录！")
        return redirect(url_for('login'))
    if request.method == "GET":
        id = request.args['id']
        cls = request.args['cls']
        sql = "delete from selectCourse where 课序号= '%s' and 开课班级='%s'" % (id, cls)
        useSQLite.insertOrDeleteOrUpdate(sql)
        return redirect(url_for('sta_changeCou_query'))


@app.route('/staff/changeCou/add', methods=["GET", "POST"])
def sta_changeCou_add():
    if session.get('exist') == None:
        flash("请登录！")
        return redirect(url_for('login'))
    if request.method == "GET":
        sql_cou = "select 课程名 from course"
        cou = useSQLite.query(sql_cou)
        sql_maj = "select 专业名 from major"
        maj = useSQLite.query(sql_maj)
        sql_cls = "select 班级名 from class"
        cls = useSQLite.query(sql_cls)
        return render_template("staff/changeCou/add.html", cou=cou, maj=maj, cls=cls)
    else:
        clsName = request.form['课程名']
        cls = useSQLite.query("select 课程编号 from course where 课程名='%s'" % clsName)[0][0]
        teaid = request.form['teaId']
        teaExist = useSQLite.query("select 姓名 from teacher where 编号='%s'" % teaid)
        if len(teaExist) == 0:
            flash("录入错误：教师编号有误!")
            sql_cou = "select 课程名 from course"
            cou = useSQLite.query(sql_cou)
            sql_maj = "select 专业名 from major"
            maj = useSQLite.query(sql_maj)
            sql_cls = "select 班级名 from class"
            cls = useSQLite.query(sql_cls)
            return render_template("staff/changeCou/add.html", cou=cou, maj=maj, cls=cls)
        teaname = teaExist[0][0]
        sel_cou = request.form['课程名']
        year = request.form['年份']
        sel_maj = request.form['开课专业']
        sel_cls = request.form['开课班级']
        peonum = request.form['人数']
        season = request.form['学期']
        cls_id = useSQLite.query("select 课程编号 from course where 课程名='%s'" % sel_cou)[0][0]
        sql_id = cls_id + teaid + year
        if season == "春季":
            sql_id += "1"
        elif season == "夏季":
            sql_id += "2"
        elif season == "秋季":
            sql_id += "3"
        elif season == "冬季":
            sql_id += "4"
        sql_insert = "insert into selectCourse values('%s', '%s', '%s','%s', %d, '%s', '%s', %d, '%s','%s', %d)" % (
            sql_id, cls_id, teaname, teaid, int(year), sel_maj, sel_cls, int(peonum), season, clsName, int(peonum))
        try:
            useSQLite.insertOrDeleteOrUpdate(sql_insert)
            sql_cou = "select 课程名 from course"
            cou = useSQLite.query(sql_cou)
            sql_maj = "select 专业名 from major"
            maj = useSQLite.query(sql_maj)
            sql_cls = "select 班级名 from class"
            cls = useSQLite.query(sql_cls)
            flash("录入信息：录入成功！")
            return render_template("staff/changeCou/add.html", cou=cou, maj=maj, cls=cls)
        except:
            flash("录入错误：该选课信息已存在，请确认！")
            sql_cou = "select 课程名 from course"
            cou = useSQLite.query(sql_cou)
            sql_maj = "select 专业名 from major"
            maj = useSQLite.query(sql_maj)
            sql_cls = "select 班级名 from class"
            cls = useSQLite.query(sql_cls)
            return render_template("staff/changeCou/add.html", cou=cou, maj=maj, cls=cls)


@app.route('/staff/changePwd/change', methods=["GET", "POST"])
def sta_changePwd_change():
    if session.get('exist') == None:
        flash("请登录！")
        return redirect(url_for('login'))
    if request.method == "GET":
        return render_template("staff/changePwd/change.html")
    else:
        staid = session.get('staid')
        old = request.form['old']
        new = request.form['new']
        # 缺少用户名
        sqlexist = "select 密码 from staff where 教工号='%s'" % staid
        oldpw = useSQLite.query(sqlexist)[0][0]
        if oldpw != old:
            flash("密码错误！")
            return redirect(url_for('sta_changePwd_change'))
        up = "update staff set 密码='%s' where 教工号 ='%s'" % (new, staid)
        useSQLite.insertOrDeleteOrUpdate(up)
        flash("修改成功！")
        return redirect(url_for('sta_changePwd_change'))


@app.route('/loginAdm', methods=['POST'])
def loginAdm():
    if session.get('exist') == None:
        flash("请登录！")
        return redirect(url_for('login'))
    return redirect(url_for('admin'))



@app.errorhandler(404)
def err_404(e):
    if session.get('exist') == None:
        flash("请登录！")
        return redirect(url_for('login'))
    else:
        if session.get('stuid') != None:
            return redirect(url_for('student'))
        if session.get('teaid') != None:
            return redirect(url_for('teacher'))
        if session.get('sta') != None:
            return redirect(url_for('staff'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
