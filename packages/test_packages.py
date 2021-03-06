# flake8: noqa
import os
from flask import Flask
from flask.testing import FlaskClient

from models import register_models # type: ignore
from package_endpoint import register_package_creator # type: ignore
import seed_packages as sp



def main():
    db_session, Package, InstallMethod = sp.init_db('sqlite:///test.db')
    sp.main(db_session, Package, InstallMethod)
    packages = [p['name'] for p in sp.load_json()]
    app, client = create_app_client()

    version = os.environ.get("INSTANCE").split(":")[0] + "_test"
    #version = "ubuntu:20.04".split(":")[0] + "_test"
    form = {"version": version,
            "packages": packages}
    resp, code, headers = client.post("/get_installer", data=form)
    assert code == "200 OK"
    resp = b"\n".join(resp)
    with open("test_script.sh", "wb+") as test_f:
        test_f.write(resp)

def create_app_client():
    db_session, Package, InstallMethod = sp.init_db('sqlite:///test.db')
    app = Flask(__name__)
    client = FlaskClient(app)
    register_package_creator(app,
                             db_session,
                             Package,
                             InstallMethod)
    return app, client

if __name__ == "__main__":
    main()
