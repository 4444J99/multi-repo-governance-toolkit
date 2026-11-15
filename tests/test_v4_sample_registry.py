import json
import os
import subprocess
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_sample_registry_missing_target_is_caught(tmp_path):
    env = dict(os.environ, REGISTRY_PATH=str(ROOT / "examples" / "sample-registry.json"),
               V4_REPORT=str(tmp_path / "v4-report.json"))
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "v4-dependency-validation.py")],
                       capture_output=True, text=True, env=env)
    assert r.returncode == 1
    assert "example-org/web -> example-org/auth (NOT IN REGISTRY)" in r.stdout
    assert "Total violations: 1" in r.stdout


def run_v4_validation(registry_dict, tmp_path):
    registry_file = tmp_path / "registry.json"
    report_file = tmp_path / "v4-report.json"
    registry_file.write_text(json.dumps(registry_dict, indent=2))

    env = dict(os.environ, REGISTRY_PATH=str(registry_file), V4_REPORT=str(report_file))
    res = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "v4-dependency-validation.py")],
        capture_output=True,
        text=True,
        env=env,
    )
    report = json.loads(report_file.read_text()) if report_file.exists() else None
    return res, report


def make_registry(edges):
    all_repos = set()
    for (f_org, f_name), (t_org, t_name) in edges:
        all_repos.add((f_org, f_name))
        all_repos.add((t_org, t_name))

    deps_by_repo = {}
    for (f_org, f_name), (t_org, t_name) in edges:
        f_key = (f_org, f_name)
        if f_key not in deps_by_repo:
            deps_by_repo[f_key] = []
        deps_by_repo[f_key].append(f"{t_org}/{t_name}")

    organs_dict = {}
    for org, name in all_repos:
        if org not in organs_dict:
            organs_dict[org] = {"repositories": []}
        deps = deps_by_repo.get((org, name), [])
        organs_dict[org]["repositories"].append({
            "org": org,
            "name": name,
            "dependencies": deps,
        })

    return {"organs": organs_dict}


@pytest.mark.parametrize(
    "from_org,to_org,is_allowed",
    [
        ("organvm-i-theoria", "organvm-ii-poiesis", True),
        ("organvm-i-theoria", "organvm-iii-ergon", True),
        ("organvm-ii-poiesis", "organvm-iii-ergon", True),
        ("organvm-ii-poiesis", "organvm-i-theoria", False),
        ("organvm-iii-ergon", "organvm-ii-poiesis", False),
        ("organvm-iii-ergon", "organvm-i-theoria", False),
    ],
)
def test_v4_cross_organ_pairs(tmp_path, from_org, to_org, is_allowed):
    registry = make_registry([((from_org, "src"), (to_org, "dst"))])
    res, report = run_v4_validation(registry, tmp_path)

    if is_allowed:
        assert res.returncode == 0
        assert report["back_edges"] == 0
        assert report["pass"] is True
    else:
        assert res.returncode == 1
        assert report["back_edges"] == 1
        assert report["pass"] is False
        assert f"Back-edge: {from_org}/src -> {to_org}/dst" in report["violations"]


@pytest.mark.parametrize("organ", ["organvm-i-theoria", "organvm-ii-poiesis", "organvm-iii-ergon"])
def test_v4_same_organ_pairs(tmp_path, organ):
    edges = [((organ, "repo1"), (organ, "repo2"))]
    registry = make_registry(edges)
    res, report = run_v4_validation(registry, tmp_path)
    assert res.returncode == 0
    assert report["back_edges"] == 0
    assert report["pass"] is True


def test_v4_self_dependency_caught(tmp_path):
    registry = {
        "organs": {
            "organvm-i-theoria": {
                "repositories": [
                    {"org": "organvm-i-theoria", "name": "repo1", "dependencies": ["organvm-i-theoria/repo1"]}
                ]
            }
        }
    }
    res, report = run_v4_validation(registry, tmp_path)
    assert res.returncode == 1
    assert report["self_deps"] == 1
    assert report["pass"] is False
    assert "Self-dep: organvm-i-theoria/repo1" in report["violations"]


def test_v4_circular_dependency_caught(tmp_path):
    registry = {
        "organs": {
            "organvm-i-theoria": {
                "repositories": [
                    {"org": "organvm-i-theoria", "name": "repo-a", "dependencies": ["organvm-i-theoria/repo-b"]},
                    {"org": "organvm-i-theoria", "name": "repo-b", "dependencies": ["organvm-i-theoria/repo-a"]},
                ]
            }
        }
    }
    res, report = run_v4_validation(registry, tmp_path)
    assert res.returncode == 1
    assert report["cycles"] >= 1
    assert report["pass"] is False
