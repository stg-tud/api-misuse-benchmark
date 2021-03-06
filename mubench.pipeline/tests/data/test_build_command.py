import logging
from unittest.mock import patch, ANY

from nose.tools import assert_equals, assert_is_instance, assert_raises, assert_in

from data.build_command import BuildCommand, MavenCommand, GradleCommand, AntCommand
from utils.shell import CommandFailedError


class BuildCommandTestImpl(BuildCommand):
    TEST_COMMAND = "-test_command-"

    @staticmethod
    def name():
        return BuildCommandTestImpl.TEST_COMMAND


class TestBuildCommand:
    def setup(self):
        self.test_subclasses = [BuildCommandTestImpl]

        self.build_command_subclasses_orig = BuildCommand.__subclasses__
        BuildCommand._get_implementations = lambda *_: self.test_subclasses

        self.logger = logging.getLogger("test")

    def teardown(self):
        BuildCommand._get_implementations = self.build_command_subclasses_orig

    def test_get_correct_command(self):
        actual = BuildCommand.create(BuildCommandTestImpl.TEST_COMMAND)
        assert_is_instance(actual, BuildCommandTestImpl)

    def test_generic_command_returns_base_implementation(self):
        uut = BuildCommand.create("-some_command-")

        assert_is_instance(uut, BuildCommand)
        assert_equals("-some_command-", uut._name)

    def test_has_no_dependencies_by_default(self):
        uut = BuildCommand.create("-some_command-")
        assert not uut._get_dependencies("-output-", "-project_dir-", self.logger)

    def test_raise_on_multiple_matches(self):
        duplicate_command = BuildCommandTestImpl.TEST_COMMAND
        self.test_subclasses = [BuildCommandTestImpl, BuildCommandTestImpl]

        assert_raises(ValueError, BuildCommand.create, duplicate_command)

    @patch("data.build_command.Shell.exec")
    def test_execute_runs_command(self, shell_mock):
        uut = BuildCommand.create("-command-")

        uut.execute("-project_dir-", self.logger)

        shell_mock.assert_called_with("-command-",
                                      cwd="-project_dir-", logger=ANY)

    @patch("data.build_command.Shell.exec")
    def test_execute_runs_command_with_args(self, shell_mock):
        command = "-command- -arg- --arg--"
        uut = BuildCommand.create(command)

        uut.execute("-project_dir-", self.logger)

        shell_mock.assert_called_with(command,
                                      cwd="-project_dir-", logger=ANY)

    def test_saves_args(self):
        uut = BuildCommand.create("-some_command- arg1 arg2")

        assert_equals(["arg1", "arg2"], uut.args)

    def test_quoted_args_are_saved_without_quotes(self):
        uut = BuildCommand.create("-some_command- 'arg 1' \"arg 2\"")

        assert_equals(["arg 1", "arg 2"], uut.args)

    @patch("data.build_command.Shell.exec")
    def test_quotes_args_for_execution(self, shell_mock):
        uut = BuildCommand.create("-command- 'arg 1'")

        uut.execute("-pdir-", self.logger)

        shell_mock.assert_called_with("-command- 'arg 1'",
                                      cwd="-pdir-", logger=ANY)

    @patch("data.build_command.Shell.exec")
    def test_raises_on_error(self, shell_mock):
        shell_mock.side_effect = CommandFailedError("-command-", "-output-")
        uut = BuildCommand.create("-some_command-")

        assert_raises(CommandFailedError, uut.execute, "-p-", self.logger)

    @patch("data.build_command.Shell.exec")
    def test_default_does_not_filter_output_on_error(self, shell_mock):
        shell_mock.side_effect = CommandFailedError("-command-", "-output-")
        uut = BuildCommand.create("-some_command-")

        try:
            uut.execute("-project_dir-", self.logger)
        except CommandFailedError as e:
            assert_equals("\n-output-", e.output)


@patch("data.build_command.shutil.copy")
@patch("data.build_command.Shell.exec")
class TestMavenCommand:
    def setup(self):
        self.logger = logging.getLogger("test")

    def test_compile_with_maven(self, shell_mock, copy_mock):
        shell_mock.return_value = """
[INFO] --- maven-dependency-plugin:2.8:build-classpath (default-cli) @ testproject ---
[INFO] Dependencies classpath:
/path/dependency1.jar:/path/dependency2.jar
[INFO] ------------------------------------------------------------------------"""

        actual_dependencies = MavenCommand("mvn", ["build"]).execute("-project_dir-", self.logger)

        assert_equals(shell_mock.mock_calls[0][1], ("mvn dependency:build-classpath -DincludeScope=compile build",))
        assert_in("/path/dependency1.jar", actual_dependencies)
        assert_in("/path/dependency2.jar", actual_dependencies)

    def test_compile_with_maven_multi_modules(self, shell_mock, copy_mock):
        shell_mock.return_value = """
    [INFO] --- maven-dependency-plugin:2.8:build-classpath (default-cli) @ module1 ---
    [INFO] Dependencies classpath:
    /path/dependency1.jar
    [INFO] ------------------------------------------------------------------------
    [INFO] --- maven-dependency-plugin:2.8:build-classpath (default-cli) @ module2 ---
    [INFO] Dependencies classpath:
    /path/dependency2.jar
    [INFO] ------------------------------------------------------------------------"""

        actual_dependencies = MavenCommand("mvn", ["build"]).execute("-project_dir-", self.logger)

        assert_equals(shell_mock.mock_calls[0][1], ("mvn dependency:build-classpath -DincludeScope=compile build",))
        assert_in("/path/dependency1.jar", actual_dependencies)
        assert_in("/path/dependency2.jar", actual_dependencies)

    def test_compile_with_maven_no_dependencies(self, shell_mock, copy_mock):
        shell_mock.return_value = """
[INFO] --- maven-dependency-plugin:2.8:build-classpath (default-cli) @ testproject ---
[INFO] Dependencies classpath:

[INFO] ------------------------------------------------------------------------"""

        MavenCommand("mvn", ["build"]).execute("-project_dir-", self.logger)

        assert_equals(shell_mock.mock_calls[0][1], ("mvn dependency:build-classpath -DincludeScope=compile build",))

    def test_filter_error_lines_from_output(self, shell_mock, copy_mock):
        full_output = """
[INFO] Scanning for projects...
[INFO] ------------------------------------------------------------------------
[INFO] BUILD FAILURE
[INFO] ------------------------------------------------------------------------
[INFO] Total time: 0.122 s
[INFO] Finished at: 2017-06-20T15:11:39+02:00
[INFO] Final Memory: 5M/176M
[INFO] ------------------------------------------------------------------------
[ERROR] No goals have been specified for this build. You must specify a valid lifecycle phase or a goal in the format <plugin-prefix>:<goal> or <plugin-group-id>:<plugin-artifact-id>[:<plugin-version>]:<goal>. Available lifecycle phases are: validate, initialize, generate-sources, process-sources, generate-resources, process-resources, compile, process-classes, generate-test-sources, process-test-sources, generate-test-resources, process-test-resources, test-compile, process-test-classes, test, prepare-package, package, pre-integration-test, integration-test, post-integration-test, verify, install, deploy, pre-clean, clean, post-clean, pre-site, site, post-site, site-deploy. -> [Help 1]
[ERROR]
[ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.
[ERROR] Re-run Maven using the -X switch to enable full debug logging.
[ERROR]
[ERROR] For more information about the errors and possible solutions, please read the following articles:
[ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/NoGoalSpecifiedException"""
        shell_mock.side_effect = CommandFailedError("mvn build", full_output)

        expected_error_output = """
[ERROR] No goals have been specified for this build. You must specify a valid lifecycle phase or a goal in the format <plugin-prefix>:<goal> or <plugin-group-id>:<plugin-artifact-id>[:<plugin-version>]:<goal>. Available lifecycle phases are: validate, initialize, generate-sources, process-sources, generate-resources, process-resources, compile, process-classes, generate-test-sources, process-test-sources, generate-test-resources, process-test-resources, test-compile, process-test-classes, test, prepare-package, package, pre-integration-test, integration-test, post-integration-test, verify, install, deploy, pre-clean, clean, post-clean, pre-site, site, post-site, site-deploy. -> [Help 1]
[ERROR]
[ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.
[ERROR] Re-run Maven using the -X switch to enable full debug logging.
[ERROR]
[ERROR] For more information about the errors and possible solutions, please read the following articles:
[ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/NoGoalSpecifiedException"""

        try:
            MavenCommand("mvn", ["build"]).execute("-project_dir-", self.logger)
        except CommandFailedError as e:
            assert_equals(expected_error_output, e.output)



@patch("data.build_command.shutil.copy")
@patch("data.build_command.Shell.exec")
class TestGradleCommand:
    def setup(self):
        self.logger = logging.getLogger("test")

    def test_compile_with_gradle(self, shell_mock, copy_mock):
        shell_mock.return_value = ":printClasspath\n/path/dependency1.jar\n/path/dependency2.jar\n\nBUILD SUCCESSFUL"

        actual_dependencies = GradleCommand("gradle", ["build"]).execute("-project_dir-", self.logger)

        assert_equals(shell_mock.mock_calls[1][1], ("gradle :printClasspath -b 'classpath.gradle'",))
        assert_in("/path/dependency1.jar", actual_dependencies)
        assert_in("/path/dependency2.jar", actual_dependencies)

    def test_compile_with_gradle_project_dir_parameter(self, shell_mock, copy_mock):
        shell_mock.return_value = ":printClasspath\n/path/dependency1.jar\n/path/dependency2.jar\n\nBUILD SUCCESSFUL"

        GradleCommand("gradle", ["build", "-p", "/testdir/"]).execute("-project_dir-", self.logger)

        assert_equals(shell_mock.mock_calls[1][1], ("gradle :printClasspath -b '/testdir/classpath.gradle'",))

    def test_compile_with_gradle_no_dependencies(self, shell_mock, copy_mock):
        shell_mock.return_value = ":printClasspath\n\nBUILD SUCCESSFUL"

        GradleCommand("gradle", ["build"]).execute("-project_dir-", self.logger)

    def test_adds_debug_flag_to_command(self, shell_mock, copy_mock):
        uut = GradleCommand("gradle", ["build"])
        assert_in("--debug", uut._prepare_args(["build"]))

    def test_filter_error_lines_from_output(self, shell_mock, copy_mock):
        full_output = """15:46:17.784 [DEBUG] [org.gradle.model.internal.registry.DefaultModelRegistry] Transitioning model element 'tasks.wrapper' to state Discovered.
15:46:17.799 [ERROR] [org.gradle.BuildExceptionReporter]
15:46:17.802 [ERROR] [org.gradle.BuildExceptionReporter] FAILURE: Build failed with an exception.abs15:46:17.811 [ERROR] [org.gradle.BuildExceptionReporter]
15:46:17.816 [ERROR] [org.gradle.BuildExceptionReporter] * What went wrong:
15:46:17.818 [ERROR] [org.gradle.BuildExceptionReporter] Could not create service of type TaskArtifactStateCacheAccess using TaskExecutionServices.createCacheAccess().
15:46:17.819 [ERROR] [org.gradle.BuildExceptionReporter] > Failed to create parent directory '/mubench/checkouts/synthetic/wait-loop/build/.gradle/2.10' when creating directory '/mubench/checkouts/synthetic/wait-loop/build/.gradle/2.10/taskArtifacts'
15:46:17.821 [ERROR] [org.gradle.BuildExceptionReporter]
15:46:17.822 [ERROR] [org.gradle.BuildExceptionReporter] * Try:
15:46:17.823 [ERROR] [org.gradle.BuildExceptionReporter] Run with --stacktrace option to get the stack trace.
15:46:17.824 [LIFECYCLE] [org.gradle.BuildResultLogger]
15:46:17.825 [LIFECYCLE] [org.gradle.BuildResultLogger] BUILD FAILED
15:46:17.826 [LIFECYCLE] [org.gradle.BuildResultLogger]
15:46:17.827 [LIFECYCLE] [org.gradle.BuildResultLogger] Total time: 3.061 secs"""
        shell_mock.side_effect = CommandFailedError("gradle build", full_output)

        expected_error_output = """
15:46:17.799 [ERROR] [org.gradle.BuildExceptionReporter]
15:46:17.802 [ERROR] [org.gradle.BuildExceptionReporter] FAILURE: Build failed with an exception.abs15:46:17.811 [ERROR] [org.gradle.BuildExceptionReporter]
15:46:17.816 [ERROR] [org.gradle.BuildExceptionReporter] * What went wrong:
15:46:17.818 [ERROR] [org.gradle.BuildExceptionReporter] Could not create service of type TaskArtifactStateCacheAccess using TaskExecutionServices.createCacheAccess().
15:46:17.819 [ERROR] [org.gradle.BuildExceptionReporter] > Failed to create parent directory '/mubench/checkouts/synthetic/wait-loop/build/.gradle/2.10' when creating directory '/mubench/checkouts/synthetic/wait-loop/build/.gradle/2.10/taskArtifacts'
15:46:17.821 [ERROR] [org.gradle.BuildExceptionReporter]
15:46:17.822 [ERROR] [org.gradle.BuildExceptionReporter] * Try:
15:46:17.823 [ERROR] [org.gradle.BuildExceptionReporter] Run with --stacktrace option to get the stack trace."""

        try:
            GradleCommand("gradle", ["build"]).execute("-project_dir-", self.logger)
        except CommandFailedError as e:
            assert_equals(expected_error_output, e.output)


@patch("data.build_command.shutil.copy")
@patch("data.build_command.Shell.exec")
class TestAntCommand:
    def setup(self):
        self.logger = logging.getLogger("test")

    def test_compile_with_ant(self, shell_mock, copy_mock):
        shell_mock.return_value = """[javac] Compilation arguments:
[javac] '-d'
[javac] '/project/build'
[javac] '-classpath'
[javac] '/project/build/classes:/path/dependency1.jar:/path/dependency2.jar'"""

        actual_dependencies = AntCommand("ant", []).execute("-project_dir-", self.logger)

        assert_equals(shell_mock.mock_calls[0][1], ("ant -debug -verbose",))
        assert_in("/path/dependency1.jar", actual_dependencies)
        assert_in("/path/dependency2.jar", actual_dependencies)

    def test_compile_with_ant_multi_build(self, shell_mock, copy_mock):
        shell_mock.return_value = """[javac] Compilation arguments:
    [javac] '-classpath'
    [javac] '/project/build:/path/dependency1.jar'
     --- some intermediate output ---
    [javac] '-classpath'
    [javac] '/path/dependency2.jar'"""

        actual_dependencies = AntCommand("ant", []).execute("-project_dir-", self.logger)

        assert_equals(shell_mock.mock_calls[0][1], ("ant -debug -verbose",))
        assert_in("/path/dependency1.jar", actual_dependencies)
        assert_in("/path/dependency2.jar", actual_dependencies)

    def test_error_outputs_error_stream(self, shell_mock, copy_mock):
        error = "-error-"
        shell_mock.side_effect = CommandFailedError("ant", "", error)

        expected_error_output = '\n' + error

        try:
            AntCommand("ant", []).execute("-project_dir-", self.logger)
        except CommandFailedError as e:
            assert_equals(expected_error_output, e.output)
