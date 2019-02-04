import os
import csv
from collections import defaultdict


class CsvFormatError(Exception):
    pass


class CsvOperations(object):
    def __init__(self, path_to_file):
        """tries to open csv file using various encodings"""
        try:
            self._process_file(path_to_file, encoding="utf-8")
        except UnicodeDecodeError:
            try:
                self._process_file(path_to_file, encoding="gbk")
            except UnicodeDecodeError:
                try:
                    self._process_file(path_to_file, encoding="gb2312", erros="replace")
                except UnicodeDecodeError:
                    raise CsvFormatError()

    def _process_file(self, path_to_file, encoding="gb2312", errors="strict"):
        """filters out unimportant rows"""
        with open(path_to_file, "r", encoding=encoding, errors=errors) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            header = [x for x in self._iter_comments(reader)]
            footer = []
            if header:
                self.column_title = header[-1]
            self.items = set()
            self.games = set()
            self.channels = set()
            self.important_rows = []
            for row in reader:
                if row[0][0] != "#":
                    if len(row[-1].split('-')) == 3:
                        try:
                            self.important_rows.append(row)
                            last_three = row[-1].strip().split('-')
                            self.items.add(last_three[0])
                            self.games.add(last_three[1][1:-1])
                            self.channels.add(last_three[2][1:-1])
                        except IndexError:
                            break
                else:
                    footer = [row]
                    break
            footer += [x for x in self._iter_comments(reader)]
            with open(os.path.join(os.getcwd(), "static/temp/filtered_" + path_to_file.split("/")[-1]), "w+") as writefile:
                writer = csv.writer(writefile, delimiter=",")
                for row in header:
                    writer.writerow(row)
                for row in self.important_rows:
                    writer.writerow(row)
                for row in footer:
                    writer.writerow(row)

    def _iter_comments(self, iterable):
        """iterates over lines that start with #"""
        temp = iter(iterable)
        next_temp = next(temp)
        while next_temp[0][0] == "#":
            yield next_temp
            next_temp = next(temp)
        yield next_temp

    def _last_three(self, remarks):
        """splits and returns last column in row"""
        last_three = remarks.split("-")
        return last_three[0], last_three[1][1:-1], last_three[2][1:-1]

    def format_check(self):
        """checks that the csv file is formatted correctly"""
        try:
            if self.column_title[4] != "发生时间" or self.column_title[-1] != "备注":
                raise CsvFormatError()
            if not self.important_rows:
                raise CsvFormatError()
        except AttributeError:
            raise CsvFormatError()
        except IndexError:
            raise CsvFormatError()


    def filter_info(self, target_game, target_channel, start_time, end_time):
        """returns a tuple according to filter parameters"""
        important_rows = self.important_rows
        income = 0
        filtered_info = []
        game_total = defaultdict(float)
        channel_total = defaultdict(float)

        if target_game == "All Games" and target_channel == "All Channels" and start_time == "" and end_time == "":
            return "No filtering done, parameters are all empty", ""

        elif target_game == "All Games":
            if not start_time:
                start_time = important_rows[0][4]
            if not end_time:
                end_time = important_rows[-1][4]
            if target_channel == "All Channels":
                for row in important_rows:
                    item, game, channel = self._last_three(row[-1])
                    row_time = row[4]
                    if start_time <= row_time <= end_time:
                        game_total[game] += float(row[6])
                    if row_time > end_time:
                        break
            else:
                for row in important_rows:
                    item, game, channel = self._last_three(row[-1])
                    row_time = row[4]
                    if target_channel == channel and start_time <= row_time <= end_time:
                        game_total[game] += float(row[6])
                    if row_time > end_time:
                        break
            return "Game totals in " + target_channel + " from {} to {}".format(start_time, end_time), \
                   [[key, "{0:.2f}".format(game_total[key])] for key in game_total]

        elif target_channel == "All Channels":
            if not start_time:
                start_time = important_rows[0][4]
            if not end_time:
                end_time = important_rows[-1][4]
            for row in important_rows:
                item, game, channel = self._last_three(row[-1])
                row_time = row[4]
                if target_game == game and start_time <= row_time <= end_time:
                    channel_total[channel] += float(row[6])
                if row_time > end_time:
                    break
            return "Channel totals in " + target_game + " from {} to {}".format(start_time, end_time), \
                   [[key, "{0:.2f}".format(channel_total[key])] for key in channel_total]

        else:
            if not start_time:
                start_time = important_rows[0][4]
            if not end_time:
                end_time = important_rows[-1][4]
            for row in important_rows:
                item, game, channel = self._last_three(row[-1])
                row_time = row[4]
                if target_game == game and target_channel == channel and start_time <= row_time <= end_time:
                    filtered_info.append(row)
                    income += float(row[6])
                if row_time > end_time:
                    break
            income = "{0:.2f}".format(income)
            return "Total income from {} from {}: {}".format(target_game, target_channel, income), filtered_info