from os import makedirs
from os.path import exists
import subprocess
from csv import reader


repo_cache_base_dir = "./data/defects4j_cache/"
if not exists(repo_cache_base_dir):
    makedirs(repo_cache_base_dir)


def get_project_root_dir(project_id, bug_id, version):
    project_root_dir = f"{repo_cache_base_dir}/{project_id}/{bug_id}/{version}"
    if exists(project_root_dir):
        return project_root_dir

    makedirs(project_root_dir)

    # checkout buggy or fixed version
    cmd = f"defects4j checkout -p {project_id} -v {bug_id}{version} -w {project_root_dir}"

    result = subprocess.run(
        cmd, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(result.stdout)
        raise RuntimeError(
            f"Failed to checkout version of {project_id} {bug_id}")

    return project_root_dir


def get_target_bugs(bugs_file):
    target_bugs = []  # list of tuples (project_id, bug_id)
    with open(bugs_file, "r") as f:
        r = reader(f)
        next(r)
        for row in r:
            project_id = row[0]
            bug_id = row[1]
            target_bugs.append((project_id, bug_id))
    return target_bugs
