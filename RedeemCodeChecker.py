from datetime import datetime, timedelta

from flask import render_template

import GameConfig
from AWSDynamoDB import AccountStorer, RedeemCodeChecker


def init():
    pass


def response(req):
    user_name = req.cookies.get("username")
    game_name_list = GameConfig.GameConfig().get_game_name_list()
    game_permission = AccountStorer().get_game_permission(user_name)
    print(game_permission)
    if req.method == "GET":
        return render_template("redeem_code_checker.html", game_names=game_name_list, permissions=game_permission)
    elif req.method == "POST":
        game_prefix = req.form['game-prefix']
        redeem_code = req.form['redeem-code']
        if game_prefix in {"zelda", "MLBT"}:
            return render_template("redeem_code_checker.html", game_names=game_name_list, permissions=game_permission,
                                   contents={"": GameConfig.GameConfig().get_game_name(game_prefix) +
                                                 " is not in the database"})
        if redeem_code:
            info = RedeemCodeChecker().get_code_info(game_prefix, redeem_code)
            if info['Redeem']:
                if info['Promo']:
                    filtered_info = {"Content:": info['Redeem'][0]['Content'],
                                     "Duration:": str(info['Redeem'][0]['Duration']),
                                     "Group:": info['Redeem'][0]['Group'],
                                     "RedeemTimestamp:": (datetime.fromtimestamp(info['Promo'][0]['RedeemTimestamp']))
                                         .strftime('%Y-%m-%d %H:%M:%S') + " UTC+0800",
                                     "UserID:": info['Promo'][0]['UserID']}
                else:
                    filtered_info = {"": "\"{}\" has not been used yet for \"{}\"".format(
                                                    redeem_code, GameConfig.GameConfig().get_game_name(game_prefix)),
                                     "Content:": info['Redeem'][0]['Content'],
                                     "Duration:": str(info['Redeem'][0]['Duration']),
                                     "Group:": info['Redeem'][0]['Group']
                                     }
            else:
                filtered_info = {"": "\"{}\" is not a valid code for \"{}\"".format(
                                       redeem_code, GameConfig.GameConfig().get_game_name(game_prefix))}
        else:
            filtered_info = {"": "No code entered"}
        return render_template("redeem_code_checker.html", game_names=game_name_list, permissions=game_permission,
                               contents=filtered_info)


if __name__ != "__main__":
    init()
