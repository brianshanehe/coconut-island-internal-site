import os
from flask import render_template, send_from_directory
from werkzeug.utils import secure_filename
import OrganizeCsv


def init():
    pass


def submit_response(req):
    """lets user upload a csv file to server"""
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "static/temp/")
    html_file = "submit_csv_file.html"
    if req.method == "GET":
        return render_template(html_file)
    elif req.method == "POST":
        file = req.files['file3']
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return render_template(html_file)


def read_response(req):
    """processes csv file and displays results according to entered parameters"""
    upload_folder = os.path.join(os.getcwd(), "static/temp/")
    file = req.path.split("/")[2]
    html_file = "read_csv_file.html"
    try:
        organized_csv = OrganizeCsv.CsvOperations(os.path.join(upload_folder, file))
        organized_csv.format_check()
    except OrganizeCsv.CsvFormatError:
        first_line = "Invalid csv file. File should be encoded as utf-8, gbk, or gb2312 and contents should be as follows:"
        error_message = [["#Any number of optional comments starting with \"#\""],
                         ["账务流水号,业务流水号,商户订单号,商品名称,发生时间,对方账号,收入金额（+元）,支出金额（-元）,账户余额（元）,交易渠道,业务类型,备注"],
                         ["Any number of rows corresponding to column title and at least one \"item-[game]-[channel]\" in the last column"]]
        return render_template(html_file, start_date="None", end_date="None", first_line=first_line, contents=error_message)
    if req.method == "GET":
        return render_template(html_file, games=organized_csv.games, channels=organized_csv.channels,
                               start_date=organized_csv.important_rows[0][4], end_date=organized_csv.important_rows[-1][4])
    elif req.method == "POST":
        game_name = req.form["game-name"]
        channel_name = req.form["channel-name"]
        start_time = req.form["start-date"]
        end_time = req.form["end-date"]
        first_line, contents = organized_csv.filter_info(game_name, channel_name, start_time, end_time)
        if contents and game_name != "All Games" and channel_name != "All Channels":
            contents = [organized_csv.column_title] + contents
        if req.form["submit"] == "Submit":
            return render_template(html_file, games=organized_csv.games, channels=organized_csv.channels,
                                   start_date=organized_csv.important_rows[0][4], end_date=organized_csv.important_rows[-1][4],
                                   first_line=first_line, contents=contents)
        elif req.form["submit"] == "Clear":
            return render_template(html_file, games=organized_csv.games, channels=organized_csv.channels,
                                   start_date=organized_csv.important_rows[0][4], end_date=organized_csv.important_rows[-1][4])
        elif req.form["submit"] == "Download":
            return send_from_directory(directory=upload_folder, filename="filtered_"+file)


if __name__ != "__main__":
    init()