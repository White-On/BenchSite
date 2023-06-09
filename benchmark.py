import os
import subprocess
import time
import json
import numpy as np
import ast
from tqdm import tqdm
from logger import logger
from structure_test import StructureTest
from pathlib import Path


class Benchmark:
    """
    Benchmark is a class that run process for each library and each task and save the results in a json file

    We expect a very specific infrastucture of file and folder in order to run the test. The infrastucture is the following:
    - pathToInfrastructure
        - targets
            - config.ini
        - tasks
            - task1
                - config.ini
                - [<beforeBuildScript>]
                - [<libraryScript>] *
                - [file(data)]
            - task2
            [...]

    Class Attributes
    ----------
    NOT_RUN_VALUE : str or int
        value that will be used in the json file if the task has not been run
    ERROR_VALUE : str or int
        value that will be used in the json file if an error occured during the task
    """

    NOT_RUN_VALUE = "NotRun"
    ERROR_VALUE = "Error"
    DEFAULT_VALUE = "Infinity"
    TIMEOUT_VALUE = "Timeout"
    DEFAULT_TIMEOUT = 40
    DEFAULT_NB_RUNS = 1
    DEBUG = False

    def __init__(self, pathToInfrastructure: str, baseResult=None) -> None:
        """
        We initialize the class by reading the config file and getting the list of library and task.
        We also initialize the results dictionary and keep the path to the infrastructure

        Parameters
        ----------
        pathToInfrastructure : str
            path to the infrastructure

        Attributes
        ----------
        pathToInfrastructure : str
            path to the infrastructure
        results : dict
            dictionary that will contain the results and will format the json file
        libraryNames : list
            list of library name
        taskNames : list
            list of task name
        dictionaryTaskInTheme : dict of list of str
            dictionary that associate a theme to a list of task
        dictonaryThemeInTask : dict of str
            dictionary that associate a task to a theme
        """

        self.pathToInfrastructure = Path(pathToInfrastructure)

        self.libraryConfig = self.GetLibraryConfig()
        self.taskConfig = self.GetTaskConfig()

        themeDirectory = self.pathToInfrastructure / "themes"

        self.libraryNames = self.libraryConfig.keys()
        self.themeNames = [
            theme.name for theme in themeDirectory.iterdir() if theme.is_dir()
        ]

        self.taskNames = []
        self.dictionaryTaskInTheme = {}
        self.dictonaryThemeInTask = {}

        # create a dictionary that associate a theme to a list of task and a dictionary that associate a task to a theme
        for themeName in self.themeNames:
            listTask = [
                task_path.name
                for task_path in themeDirectory.joinpath(themeName).iterdir()
            ]
            self.taskNames += listTask
            self.dictionaryTaskInTheme[themeName] = listTask
            for taskName in self.dictionaryTaskInTheme[themeName]:
                self.dictonaryThemeInTask[taskName] = themeName

        if baseResult is None:
            self.results = self.create_base_json()
        else:
            self.results = self.get_result_from_json(baseResult)

        logger.debug(f"{self.dictionaryTaskInTheme = }")
        logger.debug(f"{self.dictonaryThemeInTask = }")

        logger.debug(f"{self.results = }")
        logger.debug(f"{self.create_base_json() = }")

        logger.info(
            f"Library config retrieved: list of library {self.libraryConfig.keys()}"
        )
        logger.info(f"Task config retrieved: list of task {self.taskConfig.keys()}")

    def get_result_from_json(self, json_file):
        path_json = Path(json_file)
        if not path_json.exists():
            logger.error(f"File {json_file} does not exist")
            return self.create_base_json()

        # check suffix
        if path_json.suffix != ".json":
            logger.error(f"File {json_file} is not a json file")
            return self.create_base_json()

        with open(json_file, "r") as f:
            results = json.load(f)

        return results

    def create_base_json(self):
        return {
            libraryName: {
                taskName: {
                    "theme": self.dictonaryThemeInTask[taskName],
                    "results": {
                        arg: {"runtime": []}
                        for arg in self.taskConfig[taskName].get("arguments").split(",")
                    },
                }
                for taskName in self.taskNames
            }
            for libraryName in self.libraryNames
        }

    def GetLibraryConfig(self):
        strtest = StructureTest()
        libraryConfig = strtest.readConfig(
            *strtest.findConfigFile(self.pathToInfrastructure / "targets")
        )
        return libraryConfig

    def GetTaskConfig(self):
        listTaskpath = []
        strTest = StructureTest()
        listTaskpath = strTest.findConfigFile(self.pathToInfrastructure / "themes")
        taskConfig = strTest.readConfig(*listTaskpath)
        return taskConfig

    def BeforeBuildLibrary(self):
        """
        run the beforeBuild command of each library

        """

        # print("Before build library")
        logger.info(
            "Before build library ( we run the beforeBuild command of each library )"
        )
        for libraryName in self.libraryNames:
            process = subprocess.run(
                self.libraryConfig[libraryName].get("before_build"),
                shell=True,
                capture_output=True,
            )

            if process.returncode != 0:
                logger.error(f"Error in the beforeBuild command of {libraryName}")
                logger.debug(f"{process.stderr = }")
                raise Exception(
                    f"Error in the beforeBuild command of {libraryName} : {process.stderr}"
                )
            else:
                logger.info(f"Before build of {libraryName} done")

    def BeforeTask(self, taskPath: str, taskName: str):
        """
        Run the before task command/script of a task if it exist

        Parameters
        ----------
        taskPath : str
            path to the task
        taskName : str
            name of the task

        """
        beforeTaskModule = self.taskConfig[taskName].get("before_script", None)

        logger.info(f"Before task of {taskName}")
        # the beforetask might have some arguments
        kwargs = self.taskConfig[taskName].get("before_task_arguments", "{}")
        kwargs = ast.literal_eval(kwargs)
        logger.debug(f"{kwargs = }")
        if len(kwargs) == 0:
            logger.warning(
                f"No arguments for the before task command/script for {taskName}"
            )

        funcName = self.taskConfig[taskName].get("before_function", None)
        logger.debug(f"{funcName = }")
        if funcName is None:
            logger.error(
                f"No function for the before task command/script for {taskName}"
            )
            return

        relativePath = os.path.relpath(
            taskPath, os.path.dirname(os.path.abspath(__file__))
        ).replace(os.sep, ".")
        module = __import__(f"{relativePath}.{beforeTaskModule}", fromlist=[funcName])
        logger.debug(f"{module = }")
        func = getattr(module, funcName)
        logger.debug(f"{func = }")
        try:
            func(**kwargs)
        except Exception as e:
            logger.warning(f"Error in the evaluation function {funcName} of {taskName}")
            logger.debug(f"{e = }")

    def EvaluationAfterTask(
        self, moduleEvaluation, taskName: str, taskPath: str, *funcEvaluation, **kwargs
    ):
        valueEvaluation = []

        if len(funcEvaluation) == 0:
            logger.warning(f"No evaluation function for {taskName}")
            return valueEvaluation

        for funcName in funcEvaluation:
            # command = f"{self.taskConfig[taskName].get('evaluation_language')} {os.path.join(taskPath,script)} {libraryName} {arg}"

            logger.debug(
                f"Run the evaluation function {funcName} of {moduleEvaluation} for {taskName} with {kwargs}"
            )
            relativePath = os.path.relpath(
                taskPath, os.path.dirname(os.path.abspath(__file__))
            ).replace(os.sep, ".")
            module = __import__(
                f"{relativePath}.{moduleEvaluation}", fromlist=[funcName]
            )
            try:
                logger.debug(f"{module = }")
                func = getattr(module, funcName)
                logger.debug(f"{func = }")
                output = func(**kwargs)
            except Exception as e:
                logger.warning(
                    f"Error in the evaluation function {funcName} of {taskName}"
                )
                logger.debug(f"{e = }")
                output = Benchmark.ERROR_VALUE
            logger.debug(f"{output = }")
            valueEvaluation.append(output)

        return valueEvaluation

    def RunProcess(self, command, timeout, getOutput=False):
        logger.debug(f"RunProcess with the command {command}")
        if Benchmark.DEBUG:
            return np.random.randint(5) * 1.0

        start = time.perf_counter()
        try:
            process = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=timeout
            )
        except subprocess.TimeoutExpired:
            logger.warning(f"Timeout expired for the {command} command")
            return Benchmark.TIMEOUT_VALUE
        end = time.perf_counter()

        logger.debug(f"{process.stdout = }")
        logger.debug(f"{process.stderr = }")
        logger.debug(f"{process.returncode = }")

        if process.returncode == 1:
            # print(f"\nError in the {command} command")
            # print(process.stderr)
            logger.warning(f"Error in the command")
            logger.debug(f"{process.stderr = }")
            return Benchmark.ERROR_VALUE

        elif process.returncode == 2:
            # print(f"\nCan't run this task because the library doesn't support it")
            # print(process.stderr)
            logger.warning(f"Can't run this command")
            logger.debug(f"{process.stderr = }")
            return Benchmark.NOT_RUN_VALUE

        if getOutput:
            return process.stdout

        return end - start

    def CreateScriptName(self, libraryName: str, nameComplement="") -> str:
        """
        Create the name of the script that will be run for each library and task
        """
        suffix = {"python": "py", "java": "java", "c": "c", "c++": "cpp"}
        return f"{libraryName}{nameComplement}.{suffix[self.libraryConfig[libraryName].get('language', 'python')]}"

    def ScriptExist(self, scriptPath: str, scriptName: str) -> bool:
        """
        Check if the script exist in the path
        """
        script = Path(scriptPath) / scriptName
        return script.exists() and script.is_file()

    def RunTask(self, taskName: str):
        """
        Run the task for each library and save the results in the results dictionary
        """
        path = (
            self.pathToInfrastructure
            / "themes"
            / self.dictonaryThemeInTask[taskName]
            / taskName
        )

        #    We check if the before task command/script exist if not we do nothing
        beforeTaskModule = self.taskConfig[taskName].get("before_script", None)
        if beforeTaskModule is not None:
            self.BeforeTask(path, taskName)
        else:
            logger.info(f"No before task command/script for {taskName}")

        # The timeout of the task is the timeout in the config file or the default timeout
        # the timeout is in seconds
        taskTimeout = int(
            self.taskConfig[taskName].get("timeout", Benchmark.DEFAULT_TIMEOUT)
        )

        for libraryName in self.libraryNames:
            # self.results[libraryName][taskName] = {}
            # self.results[libraryName][taskName]["theme"] = self.dictonaryThemeInTask[
            #     taskName
            # ]
            # self.results[libraryName][taskName]["results"] = {}

            self.progressBar.set_description(
                f"Run task {taskName} for library {libraryName}"
            )

            self.RunTaskForLibrary(libraryName, taskName, path, timeout=taskTimeout)

    def RunTaskForLibrary(
        self, libraryName: str, taskName: str, taskPath: str, timeout: int
    ):
        arguments = self.taskConfig[taskName].get("arguments").split(",")

        # we check if the library support the task
        if not self.ScriptExist(taskPath, self.CreateScriptName(libraryName, "_run")):
            self.results[libraryName][taskName]["results"] = {
                arg: {"runtime": Benchmark.NOT_RUN_VALUE} for arg in arguments
            }
            self.progressBar.update(
                int(self.taskConfig[taskName].get("nb_runs", Benchmark.DEFAULT_NB_RUNS))
                * len(arguments)
                * 2
            )  # *2 because we have before and after run script
            return
        logger.info(f"Run task {taskName} for library {libraryName}")

        # we check if there is a before run script
        beforeRunScriptExist = self.ScriptExist(
            taskPath, self.CreateScriptName(libraryName, "_before_run")
        )
        if not beforeRunScriptExist:
            beforeRunListTime = [0]

        # we check if there is a after run script

        afterRunScript = self.taskConfig[taskName].get("evaluation_script", None)

        for arg in arguments:
            # print(f"Run task {conf.get('task_properties','name')} of library {libraryName} with argument {arg}")

            beforeRunListTime = []
            listTime = []

            total_run = int(
                self.taskConfig[taskName].get("nb_runs", Benchmark.DEFAULT_NB_RUNS)
            )

            for nb_run in range(total_run):
                # Before run script
                if beforeRunScriptExist:
                    command = f"{self.libraryConfig[libraryName].get('language')} {Path(taskPath,self.CreateScriptName(libraryName,'_before_run'))} {arg}"
                    resultProcess = self.RunProcess(command=command, timeout=timeout)
                    beforeRunListTime.append(resultProcess)
                    self.progressBar.update(1)
                    if isinstance(resultProcess, str):
                        listTime.append(resultProcess)
                        self.progressBar.update((total_run - nb_run) * 2 - 1)
                        break

                # Run script
                scriptName = self.CreateScriptName(libraryName, "_run")
                language = self.libraryConfig[libraryName].get("language")

                command = f"{language} {os.path.join(taskPath,scriptName)} {arg}"

                resultProcess = self.RunProcess(command=command, timeout=timeout)
                logger.debug(f"{resultProcess = }")
                listTime.append(resultProcess)
                self.progressBar.update(1)
                if isinstance(resultProcess, str):
                    self.progressBar.update((total_run - nb_run - 1) * 2)
                    break

            valueEvaluation = [None]

            # After run script
            if afterRunScript is not None:
                # if the script is not None, then it should be a script name or a list of script name
                functionEvaluation = self.taskConfig[taskName].get(
                    "evaluation_function", None
                )
                if functionEvaluation is not None:
                    functionEvaluation = functionEvaluation.split(" ")
                else:
                    functionEvaluation = []

                logger.debug(f"{functionEvaluation = }")

                valueEvaluation = self.EvaluationAfterTask(
                    afterRunScript,
                    taskName,
                    taskPath,
                    *functionEvaluation,
                    libraryName=libraryName,
                    filenameBif=self.taskConfig[taskName].get("file_used", ""),
                    arg=arg,
                )
                logger.debug(f"{valueEvaluation = }")
                eval = self.results[libraryName][taskName]["results"][arg].get(
                    "evaluation", {}
                )
                for i, function in enumerate(functionEvaluation):
                    element = eval.get(function, [])
                    eval = {**eval, function: element + [valueEvaluation[i]]}
                self.results[libraryName][taskName]["results"][arg]["evaluation"] = eval

            self.results[libraryName][taskName]["results"][arg]["runtime"].extend(
                [b, t] for b, t in zip(beforeRunListTime, listTime)
            )

        logger.info(f"End task {taskName} for library {libraryName}")

    def CalculNumberIteration(self):
        """
        Calculate the number of iteration for the progress bar
        """
        nbIteration = 0
        for taskName in self.taskConfig.keys():
            nbIteration += (
                int(self.taskConfig[taskName].get("nb_runs", Benchmark.DEFAULT_NB_RUNS))
                * len(self.taskConfig[taskName].get("arguments").split(","))
                * 2
                * len(self.libraryNames)
            )  # Nb runs * nb arguments * 2 (before run and after run) * nb libraries

        logger.info(f"Number of commands : {nbIteration}")
        return nbIteration

    def ConvertResultToJson(self, outputFileName="results.json"):
        """
        convert the result to a json file
        """
        with open(outputFileName, "w") as file:
            json.dump(self.results, file, indent=4)
        logger.info(f"Result saved in {outputFileName}")

    def StartAllProcedure(self):
        if not Benchmark.DEBUG:
            self.BeforeBuildLibrary()

        self.progressBar = tqdm(
            total=self.CalculNumberIteration(),
            desc="Initialization",
            ncols=150,
            position=0,
        )
        logger.info("=======Begining of the benchmark=======")
        for taskName in self.taskNames:
            self.RunTask(taskName)
        logger.info("=======End of the benchmark=======")


if __name__ == "__main__":
    currentDirectory = Path(__file__).parent.absolute()
    outputPath = currentDirectory
    result_file = currentDirectory / "results.json"
    if result_file.exists():
        run = Benchmark(
            pathToInfrastructure=currentDirectory / "repository",
            baseResult=result_file.absolute(),
        )
    else:
        run = Benchmark(pathToInfrastructure=currentDirectory / "repository")

    # run = Benchmark(pathToInfrastructure=currentDirectory / "repository")
    run.StartAllProcedure()

    # print(run.results)
    run.ConvertResultToJson(result_file.absolute())
