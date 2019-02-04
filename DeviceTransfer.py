from flask import render_template

import GameConfig
from AWSDynamoDB import AccountStorer, OperatorRecorder
from AWSS3 import DataTransfer


def init():
    pass


def response(req):
    """process device transfer request"""
    user_name = req.cookies.get("username")
    game_name_list = GameConfig.GameConfig().get_game_name_list()
    game_permission = AccountStorer().get_game_permission(user_name)

    if req.method == "GET":
        return render_template("device_transfer.html", buckets=game_name_list, permissions=game_permission)
    elif req.method == "POST":
        """buttons"""
        source_id = req.form["source-id"]
        source_ver = req.form["source-ver"]
        target_id = req.form["target-id"]
        target_ver = req.form["target-ver"]
        if req.form["bucket-name"]:
            bucket_name = GameConfig.GameConfig().get_game_bucket(req.form["bucket-name"])
        else:
            bucket_name = ""
        if req.form["submit"] == "Submit Button":
            if source_id and source_ver and target_id and target_ver:
                if bucket_name:
                    if "backup" in req.form:
                        source_results = DataTransfer().handle_read_source(bucket_name, source_id, source_ver)
                        target_results = DataTransfer().handle_read_target(bucket_name, target_id, target_ver)
                        if source_results == "Source ID exists. " and target_results == "Target ID exists. ":
                            DataTransfer().transfer_source(bucket_name, source_id, target_id, target_ver)
                            OperatorRecorder().record(user_name, "Device Transfer", GameConfig.GameConfig().get_game_name(req.form["bucket-name"]), source_id + " -> " + target_id)
                            return render_template("device_transfer.html", info="Restored from backup successfully",
                                                   buckets=game_name_list, permissions=game_permission)
                    else:
                        source_results = DataTransfer().handle_read_source(bucket_name, source_id, source_ver)
                        target_results = DataTransfer().handle_read_target(bucket_name, target_id, target_ver)
                        if source_results == "Source ID exists. " and target_results == "Target ID exists. ":
                            DataTransfer().backup_target(bucket_name, target_id, target_ver)
                            DataTransfer().transfer_source(bucket_name, source_id, target_id, target_ver)
                            OperatorRecorder().record(user_name, "Device Transfer", GameConfig.GameConfig().get_game_name(req.form["bucket-name"]), source_id + " -> " + target_id)
                            return render_template("device_transfer.html", info="Data was transferred successfully", buckets=game_name_list, permissions=game_permission)
                    return render_template("device_transfer.html", info=source_results + target_results,
                                           buckets=game_name_list, permissions=game_permission)
                return render_template("device_transfer.html", info="This game has no bucket", buckets=game_name_list, permissions=game_permission)
            else:
                return render_template("device_transfer.html", info="Not all information is given", buckets=game_name_list, permissions=game_permission)


if __name__ != "__main__":
    init()