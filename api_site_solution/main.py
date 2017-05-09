import docker
from flask import Flask, render_template
import dateutil.parser

app = Flask(__name__)


def map_status_icon(status):
    status_map = {
        "created": "fa-archive",
        "restarting": "fa-refresh",
        "running": "fa-play",
        "removing": "fa-trash-o",
        "paused": "fa-pause",
        "exited": "fa-stop",
        "dead": "fa-medkit",
    }
    if status in status_map:
        return status_map[status]
    return "fa-question"


def map_tag_label(priority):
    prio_map = {
        "1": "uk-label-danger",
        "2": "uk-label-warning",
        "3": "uk-label-success",
    }
    if priority in prio_map:
        return prio_map[priority]
    return ""


def is_tag(value):
    try:
        int(value)
    except:
        return False
    return True


def format_date(isodate):
    date = dateutil.parser.parse(isodate)
    return date.strftime("%Y.%m.%d. %H:%M")


@app.context_processor
def add_custom_processors():
    return {
        "map_status_icon": map_status_icon,
        "map_tag_label": map_tag_label,
        "is_tag": is_tag,
        "format_date": format_date,
    }


@app.route("/")
def container_list():
    client = docker.from_env()
    containers = client.containers.list(all=True)
    return render_template("container_list.html", containers=containers)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8002)
