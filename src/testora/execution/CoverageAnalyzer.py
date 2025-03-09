from dataclasses import dataclass
import io
import sqlite3
from coverage.data import CoverageData

from testora.util.Exceptions import TestoraException


@dataclass
class DiffCoverage:
    percentage_covered: float
    total_modified_lines: int
    total_covered_modified_lines: int

    def __str__(self):
        return f"Coverage: {self.percentage_covered:.2%} ({self.total_covered_modified_lines}/{self.total_modified_lines})"


def summarize_coverage(pr, test_execution, is_old_version):
    # get coverage data
    tmp_coverage_file = "coverage_report"
    with open(tmp_coverage_file, "wb") as f:
        f.write(test_execution.coverage_report)
    coverage_data = CoverageData(tmp_coverage_file)
    coverage_data.read()

    # adapt file paths from the container's file system
    project_name = pr.cloned_repo_manager.repo_name
    file_prefix = f"/home/{project_name}/"

    # check coverage for modified files
    total_modified_lines = 0
    total_covered_modified_lines = 0
    target_files = pr.non_test_modified_python_files
    for target_file in target_files:
        # get modified lines
        if is_old_version:
            modified_lines = pr.old_file_path_to_modified_lines[target_file]
        else:
            modified_lines = pr.new_file_path_to_modified_lines[target_file]

        # get covered lines
        covered_lines = coverage_data.lines(file_prefix + target_file)
        if covered_lines is None:
            # happens, e.g., when generated test doesn't invoke the tested project
            covered_lines = set()

        total_modified_lines += len(modified_lines)
        total_covered_modified_lines += len(set(modified_lines)
                                            & set(covered_lines))

    percentage_covered = total_covered_modified_lines / \
        total_modified_lines if total_modified_lines > 0 else 0

    return DiffCoverage(
        percentage_covered,
        total_modified_lines,
        total_covered_modified_lines)
