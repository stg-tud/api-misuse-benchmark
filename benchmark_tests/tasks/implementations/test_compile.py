import os
from os import makedirs
from os.path import join, exists, dirname, relpath
from shutil import rmtree
from tempfile import mkdtemp
from typing import List
from unittest.mock import MagicMock

from nose.tools import assert_equals

from benchmark.data.pattern import Pattern
from benchmark.tasks.implementations.compile import Compile
from benchmark.utils.io import create_file
from benchmark.utils.shell import CommandFailedError
from benchmark_tests.test_utils.data_util import create_version, create_project, create_misuse


class TestCompile:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.temp_dir = mkdtemp(prefix="mubench-compile-test_")
        self.project_path = join(self.temp_dir, "project")
        self.version_path = join(self.project_path, "versions", "v0")
        self.checkout_base_path = join(self.temp_dir, "checkouts")

        self.source_dir = "src"
        self.project = create_project(self.project_path, meta={"repository": {"type": "git", "url": "-url-"}})
        self.version = create_version(self.version_path, project=self.project,
                                      meta={"build": {"src": self.source_dir,
                                                      "commands": ["mkdir classes"],
                                                      "classes": "classes"},
                                            "revision": "0"},
                                      misuses=[])

        checkout = self.version.get_checkout(self.checkout_base_path)

        self.checkout_path = checkout.checkout_dir
        self.source_path = join(self.checkout_path, self.source_dir)
        makedirs(self.source_path)

        self.base_path = dirname(self.checkout_path)
        self.build_path = join(self.base_path, "build")
        self.original_sources_path = join(self.base_path, "original-src")
        self.original_classes_path = join(self.base_path, "original-classes")
        self.misuse_source_path = join(self.base_path, "misuse-src")
        self.misuse_classes_path = join(self.base_path, "misuse-classes")
        self.pattern_sources_path = join(self.base_path, "patterns-src")
        self.pattern_classes_path = join(self.base_path, "patterns-classes")

        def mock_compile(commands: List[str], cwd: str):
            source_path = join(cwd, self.source_dir)
            class_path = join(cwd, "classes")
            makedirs(class_path, exist_ok=True)
            for root, dirs, files in os.walk(source_path):
                package = relpath(root, source_path)
                for file in files:
                    file = file.replace(".java", ".class")
                    create_file(join(class_path, package, file))
                    print("fake compile: {}".format(join(class_path, package, file)))

        self.uut = Compile(self.checkout_base_path, self.checkout_base_path, False)
        self.uut._compile = MagicMock(side_effect=mock_compile)

    def teardown(self):
        rmtree(self.temp_dir, ignore_errors=True)

    def test_copies_original_sources(self):
        create_file(join(self.source_path, "a.file"))

        self.uut.process_project_version(self.project, self.version)

        assert exists(join(self.original_sources_path, "a.file"))

    def test_copies_misuse_sources(self):
        create_file(join(self.source_path, "mu.file"))
        self.version.misuses.append(create_misuse("1", meta={"location": {"file": "mu.file"}}, project=self.project))

        self.uut.process_project_version(self.project, self.version)

        assert exists(join(self.misuse_source_path, "mu.file"))

    def test_skips_copy_of_original_sources_if_copy_exists(self):
        makedirs(self.original_sources_path)
        create_file(join(self.source_path, "b.file"))

        self.uut.process_project_version(self.project, self.version)

        assert not exists(join(self.original_sources_path, "b.file"))

    def test_forces_copy_of_original_sources(self):
        makedirs(self.original_sources_path)
        create_file(join(self.source_path, "a.file"))
        self.uut.force_compile = True

        self.uut.process_project_version(self.project, self.version)

        assert exists(join(self.original_sources_path, "a.file"))

    def test_forces_clean_copy_of_original_sources(self):
        create_file(join(self.original_sources_path, "old.file"))
        self.uut.force_compile = True

        self.uut.process_project_version(self.project, self.version)

        assert not exists(join(self.original_sources_path, "old.file"))

    def test_copies_pattern_sources(self):
        self.create_misuse_with_pattern("m", "a.java")

        self.uut.process_project_version(self.project, self.version)

        assert exists(join(self.pattern_sources_path, "m", "a.java"))

    def test_skips_copy_of_pattern_sources_if_copy_exists(self):
        self.create_misuse_with_pattern("m", "a.java")
        makedirs(join(self.pattern_sources_path, "m"))

        self.uut.process_project_version(self.project, self.version)

        assert not exists(join(self.pattern_sources_path, "m", "a.java"))

    def test_forces_copy_of_pattern_sources(self):
        self.create_misuse_with_pattern("m", "a.java")
        makedirs(join(self.pattern_sources_path, "m"))
        self.uut.force_compile = True

        self.uut.process_project_version(self.project, self.version)

        assert exists(join(self.pattern_sources_path, "m", "a.java"))

    def test_skips_copy_of_pattern_sources_if_no_pattern(self):
        self.create_misuse_with_pattern("mwp", "a.java")
        makedirs(join(self.pattern_sources_path, "mwp"))
        self.version._MISUSES.append(create_misuse("mwop", project=self.project))

        self.uut.process_project_version(self.project, self.version)

        assert not exists(join(self.pattern_sources_path, "mwp", "a.java"))

    def test_skips_if_no_config(self):
        del self.version._YAML["build"]

        response = self.uut.process_project_version(self.project, self.version)

        assert_equals([self.version.id], response)

    def test_passes_compile_commands(self):
        self.version._YAML["build"]["commands"] = ["a", "b"]

        self.uut.process_project_version(self.project, self.version)

        self.uut._compile.assert_called_with(["a", "b"], self.build_path)

    def test_copies_additional_sources(self):
        create_file(join(self.version_path, "compile", "additional.file"))

        self.uut.process_project_version(self.project, self.version)

        assert exists(join(self.build_path, "additional.file"))

    def test_skips_compile_if_classes_exist(self):
        makedirs(self.original_classes_path)
        create_file(join(self.source_path, "some.file"))

        self.uut.process_project_version(self.project, self.version)

        assert not exists(join(self.original_classes_path, "some.file"))

    def test_forces_compile(self):
        makedirs(self.original_classes_path)
        create_file(join(self.source_path, "some.file"))
        self.uut.force_compile = True

        self.uut.process_project_version(self.project, self.version)

        assert exists(join(self.original_classes_path, "some.file"))

    def test_skips_on_build_error(self):
        self.uut._compile.side_effect = CommandFailedError("-cmd-", "-error message-")

        response = self.uut.process_project_version(self.project, self.version)

        assert_equals([self.version.id], response)

    def test_copies_misuse_classes(self):
        create_file(join(self.source_path, "mu.java"))
        self.version.misuses.append(create_misuse("1", meta={"location": {"file": "mu.java"}}, project=self.project))

        self.uut.process_project_version(self.project, self.version)

        assert exists(join(self.misuse_classes_path, "mu.class"))

    def test_compiles_patterns(self):
        self.create_misuse_with_pattern("m", "a.java")

        self.uut.process_project_version(self.project, self.version)

        assert exists(join(self.pattern_classes_path, "m", "a.class"))

    def test_compiles_patterns_in_package(self):
        self.create_misuse_with_pattern("m", join("a", "b.java"))

        self.uut.process_project_version(self.project, self.version)

        assert exists(join(self.pattern_classes_path, "m", "a", "b.class"))

    def test_skips_compile_patterns_if_pattern_classes_exist(self):
        self.create_misuse_with_pattern("m", "a.java")
        makedirs(join(self.pattern_classes_path, "m"))

        self.uut.process_project_version(self.project, self.version)

        assert not exists(join(self.pattern_classes_path, "m", "a.class"))

    def test_forces_compile_patterns(self):
        self.create_misuse_with_pattern("m", "a.java")
        makedirs(join(self.pattern_classes_path, "m"))
        self.uut.force_compile = True

        self.uut.process_project_version(self.project, self.version)

        assert exists(join(self.pattern_classes_path, "m", "a.class"))

    def test_skips_compile_patterns_if_no_pattern(self):
        self.create_misuse_with_pattern("mwp", "a.java")
        makedirs(join(self.pattern_classes_path, "mwp"))
        self.version._MISUSES.append(create_misuse("mwop", project=self.project))

        self.uut.process_project_version(self.project, self.version)

        assert not exists(join(self.pattern_classes_path, "mwp", "a.class"))

    def create_misuse_with_pattern(self, misuse_id, pattern_file):
        misuse = create_misuse(misuse_id, project=self.project)
        create_file(join(self.source_path, misuse.location.file))
        misuse._PATTERNS = {self.create_pattern(pattern_file)}
        self.version._MISUSES = [misuse]

    def create_pattern(self, filename):
        pattern = Pattern(self.temp_dir, filename)
        create_file(pattern.path)
        return pattern
