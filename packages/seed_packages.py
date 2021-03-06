from collections import defaultdict      # noqa: F401
import json
import os
import subprocess
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from models import register_models  # type: ignore


def load_json():
    try:
      os.chdir("packages")
      sub = True
    except:    # noqa: E722
      sub = False
      raise

    with open("packages.json") as json_f:
      packages = json.load(json_f)

    if sub:
      os.chdir("..")

    return packages


def init_db(uri):
    engine = create_engine(uri, convert_unicode=True)
    db_session = scoped_session(sessionmaker(autocommit=False,
                                             autoflush=False,
                                             bind=engine))
    Base = declarative_base()
    Base.query = db_session.query_property()
    Package, InstallMethod = register_models(Base)
    Base.metadata.create_all(bind=engine)
    return db_session, Package, InstallMethod


def convert_icons():
  os.chdir("static/images")
  subprocess.check_call("./convert.sh")
  os.chdir("../..")


def parse_packages(package_list, db_session, Package, InstallMethod):
  packages = db_session.query(Package).delete()
  install_methods = db_session.query(InstallMethod).delete()
  try:
    db_session.commit()
  except Exception as e:
    print("FAILED!", file=sys.stderr)
    print(str(e), file=sys.stderr)
    db_session.rollback()

  print("========================", file=sys.stderr)
  print("deleting {} packages".format(packages), file=sys.stderr)
  print("deleting {} install_methods".format(install_methods), file=sys.stderr)
  print("========================", file=sys.stderr)

  for p in package_list:
    p_obj = Package(name=p['name'],
                    description=p['description'],
                    icon_url=p['icon_url'],
                    category=p['category'])
    methods = []
    for t, c in p['installers'].items():
      m = InstallMethod(method_type=t,
                        pre_install="\n".join(c['pre_install']),
                        package_name=c['package_name'],
                        post_install="\n".join(c['post_install']))
      m.package = p_obj
      methods.append(m)
    db_session.add(p_obj)
    [db_session.add(m) for m in methods]
    db_session.commit()


def main(db_session, Package, InstallMethod):
  j = load_json()
  parse_packages(j, db_session, Package, InstallMethod)


if __name__ == "__main__":
  if len(sys.argv) > 1:
    uri = sys.argv[1]
  else:
    uri = 'sqlite:///test.db'
  db_session, Package, InstallMethod = init_db(uri)
  main(db_session, Package, InstallMethod)
